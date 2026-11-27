# WP-102 external Runner 独立复核证据

受测产品提交：`e7618b5a535e67aaca6aef7d5dfe30d3eb0b6291`。本目录由非产品实现者整理；两次运行各创建全新隔离目录，没有重复执行已有 experiment。只验证有限合成本地执行，不代表真实供应商、云端或业务验收。

| 实测项 | 结果 | 证据 |
|---|---|---|
| 两个 Worker 并行 | 实际 PID 40117 / 40118；共享 OS 时钟区间交集 **2,005,497,000 ns**；各 exit 0 | [原始观测的公开副本](parallel/verified-result.json) |
| 受控交付 | 两份内容、baseline、assignment、epoch/token 均匹配；`accepted=false` | [最终权威快照](parallel/authority-final.json) |
| 执行中撤销 | 实际进程退出；assignment=`revoked`、workspace=`stopped`、WP=`paused`；零交付 | [撤销结果](revoke/verified-result.json)、[权威快照](revoke/authority-final.json) |
| 外层 A01 | 两轮各 8 项检查通过；包括可信目录写/硬链接、仓库写、外部读写、空 C 根删除、网络拒绝及凭证环境缺席 | 两场景的 `prepared.json` |
| 实际内层策略 | T 配置/receipt、C 权威、checkout 的读写及网络共 9 项均 EPERM；仅自身 scratch 唯一 canary 写入成功 | [内层策略探针](inner-policy-result.json) |
| 控制器负例 | 独立运行 21 项全部通过；使用明确标注的合成 receipt，不冒充进程执行证据 | [测试日志](controller-negative-tests/stderr.log) |

每场景 13 份产品源码/Schema/入口的内容哈希逐一匹配上述 Git 提交。控制器负例的六份受测文件另有 [commit 绑定](controller-negative-tests/commit-binding.json)。全部实际配置、命令、退出码、请求、receipt、stdout/stderr、策略和最终权威快照随场景保留；受保护原日志的摘要在导出前由可信协调器重新核验。

## 两项被发现并纠正的证据问题

旧 host reader 的“先 resolve、再仅对末级 O_NOFOLLOW”存在祖先换链竞态。独立副本改为逐段目录 FD + O_NOFOLLOW；已用无敏感内容的真实文件操作复现旧 reader 读到外部 canary，并验证新版拒绝。同一探针验证已固定父 FD 后换链仍读原目录，以及硬链接/FIFO 拒绝。见 [结果](reader-probe-result.json) 和 [差异](harness/reader-hardening.diff)。该加固只涉及仓库外测试协调器，未改变产品权限。

旧 Worker 使用的 macOS Python 3.9 `monotonic_ns()` 不能据此进行跨进程区间比较，先前基于它的重叠推断已撤回。[Python 官方版本说明](https://docs.python.org/3.10/library/time.html#time.monotonic) 说明 macOS 的相关变化发生于 3.10。本次 Worker 使用 `clock_gettime_ns(CLOCK_MONOTONIC)`；独立实测串行对照不重叠、并行对照重叠，四个子进程区间均落在父进程同一 OS 时钟的包围区间内。见 [时钟对照](clock-control/observations.json)。本结论仅限本机，不声称跨主机时钟同步。

## 审核与执行边界

- 固定 Driver SHA256：`cfb917f6b039ec3de24bcc2c6c41fba314cb3945d4cb01387b311e0f1f2db2ce`。
- 固定 Worker SHA256：`05188893d5f9d87f3bd9d7c44e3e82be8c7c53293d538c02742fd8204dfee97d`。
- 独立协调器原始 SHA256：`9e0e324b2e58fadfe485d21cb41c9554f88f06d28ab6db44e817af972e54ca5f`；新增 host reader 与撤销三状态断言经 Project Lead 复核此固定哈希后执行。
- 协调器只使用 stdlib，宿主不 import 候选产品；候选控制器始终在外层 Seatbelt。固定 Worker 使用独立 Seatbelt。
- 内层探针使用本次 Driver 真实生成的原策略，运行固定系统 Python 探针，无候选 import、新 Worker 或新配置。写权限检测只打开已有文件后关闭，不截断或写入；唯一实际写入为新 scratch canary。原配置、receipt、权威、源码、策略及 stdout/stderr 前后哈希不变。
- 独立复跑复用已审查的候选 CLI harness；它是非作者执行，不声称测试设计全部独立。这里的配置路径声明本身也不能证明可信目录不可写，必须结合实际 OS 边界与原始 receipt 核查。

## 脱敏及哈希解释

[导出清单](export-manifest.json) 为每份原始证据记录 **original_sha256** 与 **public_sha256**。本机路径替换为 `<REPOSITORY>`、`<EXPERIMENT>`、`<PYTHON_DEPS>`、`<LOCAL_EVIDENCE>`；证据 JSON 内原有 `config_sha256`、日志摘要等继续指向原始字节，不能直接与脱敏配置字节比较。

`.py.txt` 和 `.sb.txt` 是审核用公开副本，路径占位符须还原后才能复现；不能将公开副本哈希当成当时执行的原始哈希。fixture 的 principal、session、epoch、token 均为公开合成数据，没有个人登录凭证。`verification-summary.json` 与本 README 是汇总说明，不是原始执行日志。
