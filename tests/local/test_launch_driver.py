"""Pure validation and Fake Popen tests; not a real launcher acceptance run."""
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest

from framework.local.launch_driver import Driver, canonical_sha, policy, strict_json, validate_config, validate_request


class Input:
    def __init__(self):
        self.reader, writer = os.pipe()
        self.writer = os.fdopen(writer, 'wb')
        self.saved = b''
    def fileno(self):
        return self.writer.fileno()
    def close(self):
        self.writer.close()
    @property
    def payload(self):
        os.set_blocking(self.reader, False)
        while True:
            try:
                chunk = os.read(self.reader, 65536)
            except BlockingIOError:
                break
            if not chunk:
                break
            self.saved += chunk
        return self.saved


class Child:
    def __init__(self, pid):
        self.pid = pid; self.stdin = Input(); self.returncode = None
    def poll(self):
        return self.returncode
    def wait(self, timeout):
        if self.returncode is None:
            raise subprocess.TimeoutExpired('fake', timeout)
        return self.returncode


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.trusted = self.root / 'trusted'; self.trusted.mkdir()
        self.candidate = self.root / 'candidate'; self.candidate.mkdir()
        self.requests = self.candidate / 'requests'; self.requests.mkdir()
        self.receipts = self.trusted / 'receipts'; self.receipts.mkdir()
        self.scratch = self.trusted / 'workers'; self.scratch.mkdir()
        self.worker = self.trusted / 'fixed_worker.py'; self.worker.write_text('fixed synthetic fixture, never executed')
        self.workspace = self.candidate / 'workspace'; self.workspace.mkdir(); (self.workspace / 'src').mkdir()
        self.job = dict(job_id='job-a', operation_id='operation-a', workspace=str(self.workspace), output='src/out',
                        content_sha256=hashlib.sha256('中文'.encode()).hexdigest(), max_delay_seconds=2, max_runtime_seconds=5)
        self.config = dict(format='v4-launch-config/1', batch_id='batch', trusted_root=str(self.trusted),
            candidate_root=str(self.candidate),
            driver_sha256='a'*64, python='/usr/bin/python3', worker_program=str(self.worker),
            worker_sha256=hashlib.sha256(self.worker.read_bytes()).hexdigest(), request_dir=str(self.requests),
            receipt_dir=str(self.receipts), scratch_root=str(self.scratch), deadline_seconds=10, jobs=[self.job])
        self.request = dict(format='v4-launch-request/1', job_id='job-a', operation_id='operation-a',
                            content='中文', delay_seconds=1, timeout=4)
        self.children=[]; self.spawns=[]; self.signals=[]; self.clock_value=0
        self.driver=Driver(self.config,popen=self.spawn,killpg=self.kill,clock=lambda:self.clock_value)
        self.addCleanup(os.close,self.driver.request_fd)
        self.addCleanup(lambda:[s.close() for streams in self.driver.streams.values() for s in streams])
        self.addCleanup(lambda:[(c.stdin.close(),os.close(c.stdin.reader)) for c in self.children])

    def spawn(self, argv, **kwargs):
        self.spawns.append((argv,kwargs)); child=Child(100+len(self.children)); self.children.append(child)
        kwargs['stdout'].write(b'actual fake stdout\n'); kwargs['stdout'].flush()
        return child

    def kill(self,pid,signum):
        self.signals.append((pid,signum))
        for child in self.children:
            if child.pid==pid: child.returncode=-signum

    def write(self,value=None,name='job-a.request.json'):
        (self.requests/name).write_text(json.dumps(self.request if value is None else value))

    def record(self):
        return json.loads((self.receipts/'job-a.json').read_text())

    def test_utf8_request_hash_matches_canonical_protocol(self):
        expected=hashlib.sha256(json.dumps(self.request,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(validate_request(self.request,self.job),expected)

    def test_strict_json_rejects_duplicates_and_nonfinite(self):
        for data in ['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}']:
            with self.subTest(data=data),self.assertRaises(ValueError):strict_json(data)

    def test_request_rejects_command_environment_and_policy(self):
        for key in ['argv','env','policy','workspace']:
            value=dict(self.request);value[key]='not allowed'
            with self.subTest(key=key),self.assertRaises(ValueError):validate_request(value,self.job)

    def test_request_is_bound_to_operation_content_and_limits(self):
        for key,value in [('job_id','other'),('operation_id','other'),('content','other'),('delay_seconds',True),('delay_seconds',3),('timeout',False),('timeout',6)]:
            bad=dict(self.request);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_request(bad,self.job)

    def test_config_rejects_duplicate_workspace_and_bad_job_id(self):
        cfg=copy.deepcopy(self.config);other=dict(self.job,job_id='job-b',operation_id='other');cfg['jobs'].append(other)
        with self.assertRaisesRegex(ValueError,'duplicate'):validate_config(cfg)
        cfg=copy.deepcopy(self.config);cfg['jobs'][0]['job_id']='../escape'
        with self.assertRaises(ValueError):validate_config(cfg)

    def test_config_rejects_nested_workspaces(self):
        nested=self.workspace/'src';(nested/'src').mkdir()
        cfg=copy.deepcopy(self.config)
        cfg['jobs'].append(dict(self.job,job_id='job-b',operation_id='operation-b',workspace=str(nested)))
        with self.assertRaisesRegex(ValueError,'duplicate'):validate_config(cfg)

    def test_config_rejects_trust_overlap(self):
        for field,value in [('request_dir',str(self.scratch)),('scratch_root',str(self.receipts)),('receipt_dir',str(self.root)),('candidate_root',str(self.root))]:
            cfg=dict(self.config);cfg[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_config(cfg)

    def test_worker_hash_and_hardlink_fail_closed(self):
        self.worker.write_text('changed')
        with self.assertRaisesRegex(ValueError,'hash'):validate_config(self.config)
        os.link(self.worker,self.trusted/'alias')
        with self.assertRaisesRegex(ValueError,'single-link'):validate_config(self.config)

    def test_request_symlink_and_hardlink_refused(self):
        path=self.requests/'job-a.request.json';outside=self.root/'payload';outside.write_text(json.dumps(self.request))
        path.symlink_to(outside)
        self.driver.tick();self.assertEqual(self.record()['state'],'rejected');self.assertEqual(self.spawns,[])
        path.unlink();os.link(outside,path)
        with self.assertRaisesRegex(ValueError,'unsafe request'):self.driver.mailbox(path.name)

    def test_mailbox_pins_original_directory(self):
        renamed=self.root/'old-requests';self.requests.rename(renamed)
        other=self.root/'other';other.mkdir();(other/'job-a.request.json').write_text(json.dumps(self.request))
        self.requests.symlink_to(other)
        self.assertIsNone(self.driver.mailbox('job-a.request.json'))

    def test_mailbox_rejects_fifo_without_blocking(self):
        os.mkfifo(self.requests/'job-a.request.json')
        with self.assertRaisesRegex(ValueError,'unsafe request'):self.driver.mailbox('job-a.request.json')

    def test_real_launch_arguments_are_fixed_but_process_is_fake(self):
        self.write();self.driver.tick();r=self.record()
        self.assertEqual(r['state'],'running');self.assertEqual(r['request_sha256'],canonical_sha(self.request));self.assertEqual(r['operation_id'],'operation-a')
        argv,kw=self.spawns[0]
        self.assertEqual(argv[:2],['/usr/bin/sandbox-exec','-f']);self.assertEqual(argv[3:],['/usr/bin/python3','-I','-B','-S',str(self.worker)])
        self.assertEqual(set(kw['env']),{'HOME','TMPDIR','PATH','PYTHONNOUSERSITE','PYTHONDONTWRITEBYTECODE','LANG'})
        self.assertEqual(json.loads(self.children[0].stdin.payload),dict(path='src/out',content='中文',delay_seconds=1))
        self.children[0].returncode=0;self.driver.tick();done=self.record()
        self.assertEqual(done['state'],'finished');self.assertEqual(done['exit_code'],0);self.assertGreater(done['sequence'],r['sequence'])
        self.assertEqual(done['stdout_sha256'],hashlib.sha256(b'actual fake stdout\n').hexdigest())
        self.driver.tick();self.assertEqual(len(self.spawns),1)

    def test_failure_exit_is_not_success(self):
        self.write();self.driver.tick();self.children[0].returncode=71;self.driver.tick()
        self.assertEqual(self.record()['exit_code'],71);self.assertEqual(self.record()['state'],'finished')

    def test_cancel_observes_owned_child_exit(self):
        self.write();self.driver.tick()
        self.write(dict(format='v4-launch-cancel/1',job_id='job-a',request_sha256=canonical_sha(self.request)),'job-a.cancel.json')
        self.driver.tick();r=self.record()
        self.assertEqual(self.signals,[(100,signal.SIGTERM)]);self.assertEqual(r['state'],'stopped');self.assertEqual(r['exit_code'],-signal.SIGTERM)

    def test_cancel_before_launch_never_spawns(self):
        self.write()
        self.write(dict(format='v4-launch-cancel/1',job_id='job-a',request_sha256=canonical_sha(self.request)),'job-a.cancel.json')
        self.driver.tick()
        self.assertEqual(self.record()['state'],'rejected');self.assertEqual(self.spawns,[])
        self.assertIsNone(self.record()['pid']);self.assertIsNone(self.record()['exit_code'])

    def test_changed_request_cannot_relaunch_same_slot(self):
        self.write();self.driver.tick();self.children[0].returncode=0;self.driver.tick()
        prior=self.record();self.write(dict(self.request,operation_id='other'));self.driver.tick()
        self.assertEqual(self.record(),prior);self.assertEqual(len(self.spawns),1)

    def test_timeout_observes_owned_child_exit(self):
        self.write();self.driver.tick();self.clock_value=5;self.driver.tick()
        self.assertEqual(self.record()['state'],'stopped');self.assertEqual(self.signals,[(100,signal.SIGTERM)])

    def test_nonreading_pipe_cannot_block_runtime_timeout(self):
        content='x'*65536
        self.job['content_sha256']=hashlib.sha256(content.encode()).hexdigest()
        self.request['content']=content
        self.write();self.driver.tick()
        for _ in range(40):self.driver.tick()
        self.assertIn('job-a',self.driver.pending_input)
        self.clock_value=5;self.driver.tick()
        self.assertEqual(self.record()['state'],'stopped')
        self.assertEqual(self.signals,[(100,signal.SIGTERM)])

    def test_unconfirmed_stop_is_unknown(self):
        self.write();self.driver.tick();self.driver.killpg=lambda pid,sig:None;self.clock_value=5;self.driver.tick()
        self.assertEqual(self.record()['state'],'unknown');self.assertIsNone(self.record()['exit_code'])

    def test_restarted_launch_is_unknown_without_signal_or_spawn(self):
        self.write();self.driver.tick()
        replacement=Driver(self.config,popen=self.spawn,killpg=self.kill);self.addCleanup(os.close,replacement.request_fd)
        replacement.restore();replacement.tick()
        self.assertEqual(self.record()['state'],'unknown');self.assertEqual(self.signals,[]);self.assertEqual(len(self.spawns),1)
        for streams in self.driver.streams.values():
            for stream in streams:stream.close()

    def test_restore_rejects_different_config_bytes(self):
        self.write();self.driver.tick();self.children[0].returncode=0;self.driver.tick()
        replacement=Driver(self.config,popen=self.spawn,killpg=self.kill,config_sha256='b'*64)
        self.addCleanup(os.close,replacement.request_fd)
        with self.assertRaisesRegex(ValueError,'receipt identity mismatch'):replacement.restore()
        self.assertEqual(len(self.spawns),1);self.assertEqual(self.signals,[])

    def test_two_fixed_slots_have_distinct_processes_and_receipts(self):
        second_workspace=self.candidate/'workspace-b';second_workspace.mkdir();(second_workspace/'src').mkdir()
        second=dict(self.job,job_id='job-b',operation_id='operation-b',workspace=str(second_workspace))
        cfg=dict(self.config,jobs=[self.job,second])
        driver=Driver(cfg,popen=self.spawn,killpg=self.kill,clock=lambda:self.clock_value)
        self.addCleanup(os.close,driver.request_fd)
        self.addCleanup(lambda:[s.close() for streams in driver.streams.values() for s in streams])
        self.write();self.write(dict(self.request,job_id='job-b',operation_id='operation-b'),'job-b.request.json')
        driver.tick();self.assertEqual(len(self.children),2)
        for child in self.children:child.returncode=0
        driver.tick()
        receipts=[json.loads((self.receipts/(job+'.json')).read_text()) for job in ('job-a','job-b')]
        self.assertNotEqual(receipts[0]['pid'],receipts[1]['pid'])
        self.assertTrue(all(r['state']=='finished' and r['exit_code']==0 for r in receipts))

    def test_spawn_exception_preserves_launch_intent_as_unknown(self):
        def fail(*a,**kw):raise OSError('lost launch result')
        self.driver.popen=fail;self.write();self.driver.tick()
        self.assertEqual(self.record()['state'],'unknown');self.driver.tick();self.assertEqual(self.spawns,[])
        for streams in self.driver.streams.values():
            for stream in streams:stream.close()

    def test_policy_has_no_network_or_controller_authority_grant(self):
        p=policy(self.job,str(self.worker),self.scratch/'job-a',str(self.candidate))
        self.assertIn('(deny default)',p);self.assertNotIn('(allow network',p)
        self.assertNotIn(str(self.receipts),p);self.assertNotIn(str(self.requests),p)
        self.assertIn(str(self.workspace/'src/out'),p)
        self.assertIn('(require-all (subpath '+json.dumps(str(self.candidate))+')',p)
        read_rule=next(line for line in p.splitlines() if line.startswith('(allow file-read*'))
        self.assertNotIn(str(self.workspace),read_rule)


if __name__=='__main__':unittest.main()
