# External Runner：四种真实有限场景

本目录保存研发侧第一轮真实集成记录，产品源码逐文件绑定提交 `e7618b5a535e67aaca6aef7d5dfe30d3eb0b6291`，见 [source-binding.json](source-binding.json)。不代替后续独立运行、Owner 阶段放行或整套 V4 验收。

这次实际执行了公开 `run-external` CLI、真实 Store/worktree、外部已审核 driver、OS 沙盒内固定 Worker 和受控 submit；不是 Fake RPC 或合成 terminal receipt。四个实验各使用全新的隔离目录，仅一次宿主启动，原始现场完整保留在仓库外。

| 场景 | candidate harness / driver 退出 | 真实 Worker 退出 | 交付 | 结果 |
|---|---|---|---:|---|
| [single](single/verified-result.json) | 0 / 0 | 0 | 1 | 固定任务真实写入，fenced submit 返回 accepted=false |
| [parallel](parallel/verified-result.json) | 0 / 0 | 0、0 | 2 | 两个独立 worktree、两次真实 CLI、两份各自身份绑定的交付 |
| [failure](failure/verified-result.json) | 0 / 0 | 1 | 0 | 只读合成目标使真实写入失败；CLI 非零，回放仍非零 |
| [revoke](revoke/verified-result.json) | 0 / 0 | -15 | 0 | 撤权触发 cancel，driver 确认真实退出后记录 stopped |

负例的 harness/driver 退出 0 表示正确验证了失败行为，不表示 Worker 成功。所有交付仍为 `accepted=false`；没有工程或业务验收被自动推进。

## 两个任务的实际时间记录

两个公开 CLI 的 request 均落地后，协调器才启动有限 driver。没有根据线程存在或 PID 不同推断并行。

固定 Worker 通过 `time.clock_gettime_ns(time.CLOCK_MONOTONIC)` 记录读取任务后、sleep 前的开始时间，以及写文件后的结束时间；日志中的 PID 与受保护 driver receipt 的 PID 一一匹配。避免使用本机 Python 3.9 的进程相对 `monotonic_ns()` 跨进程比较。

| Worker PID | started_ns | finished_ns |
|---:|---:|---:|
| 39093 | 152266525044000 | 152268525929000 |
| 39094 | 152266527037000 | 152268537344000 |

实测 `min(finished_ns) - max(started_ns) = 1,998,892,000 ns`。这是本次两个固定合成任务（含 2 秒 delay）的观测区间重叠，不代表真实模型 Coding Agent 的生产并发性能。原日志见 [job-a](parallel/logs/job-a/stdout.log.txt)、[job-b](parallel/logs/job-b/stdout.log.txt)，driver 生命周期记录另存于结果，不与 Worker 自报时钟混为一项数据。

## 回放与撤权状态

[replay-summary.json](replay-summary.json) 关联第一次 CLI 返回与同 operation 的回放。成功结果保持相同，失败/撤权回放仍非零。已执行、固定哈希的 harness 逐次断言回放前后 authority 与受保护 receipt 字节不变；没有再次调用协调器执行同一实验。第一次结果保存于各场景 `candidate-result.json`，回放命令记录在 `commands/`；同名 attempt 文件可能由回放替换，第一次返回仍由 `outputs` 独立保留。

[state-checks.json](state-checks.json) 是实验结束后额外只读补证：revoke 的持久化 authority 明确为 Assignment `revoked`、workspace `stopped`、Work Package `paused`、delivery 数 0。它不是当前可继续执行的权限证明。driver 真实退出码为 -15；cancel 文件本身没有被当作停止证据。

failure 保留了进程 `finished / exit_code=1`，Work Package 仍未验收；没有把“进程已经退出”当作任务完成。

## A01 边界及已知限制

宿主只运行纯 stdlib 协调器和独立审核后按准确哈希复制的 driver；没有宿主导入候选模块。driver 为 `cfb917f6b039ec3de24bcc2c6c41fba314cb3945d4cb01387b311e0f1f2db2ce`，固定 Worker 为 `05188893d5f9d87f3bd9d7c44e3e82be8c7c53293d538c02742fd8204dfee97d`。宿主执行需要显式匹配这两个审核哈希。

候选 fixture、Store 和 CLI 全在外层 Seatbelt：C 是唯一可写根，T、仓库与依赖只读；明确拒绝 unlink C 根。四场景都实际通过 8 项 canary：写 T、T 硬链接别名、写仓库、读/写外部无害文件、删除空 C 根、连网及凭证环境不存在。

macOS Python 启动实际在 C 中生成了 499 字节 `xcrun_db`。harness 仅删除这个精确名字、常规单链接且受大小限制的启动缓存，记录其指纹；其他未知文件会保留并失败。随后确认 C 确实为空，再验证根目录删除得到权限拒绝，没有把 ENOTEMPTY 当作隔离成功。事实见各场景 `prepared.json` 的 `startup_cleanup`。

**初版协调器是本次合作 fixture 的测试工具，不是已验收的恶意候选读取边界。** 后续独立复核发现其宿主 `regular()` 在 resolve 与 open 之间没有逐段 dir_fd 固定祖先，因此不覆盖恶意 C 目录换链的 TOCTOU 攻击。此次具体 harness 没有执行该攻击；不能从这四场景或 canary 推导出宿主 reader 对恶意候选安全。加固协调器及新的独立实验由同级 independent 证据另行记录；本目录保留初版真实代码与结果，不改写运行历史。

这些实验没有调用模型、联网、启用费用、创建生产调度服务、修改 main、合入或发布。真实供应商接管、云端恢复和业务验证均不在本目录验收范围。

## 文件与脱敏

每个场景保留 manifest/config、公开 CLI 命令和输入、真实 request/cancel、原 driver receipt、受保护原日志、authority、结果及输入/程序指纹。`coordinator.py.txt` 与 `candidate_harness.py.txt` 是本次实际代码副本，仅供审查，不能未经复核部署为通用执行平台。没有复制 Git 目录或整个 worktree。

本机 workspace、依赖、实验目录和协调器目录仅替换为明确占位符；stdout/stderr 使用 `.log.txt` 保存公开副本。`artifact-index.json` 分别记录原始字节与公开副本 SHA-256。config/receipt 内的 hash 仍指向原始运行字节，不应拿它与路径脱敏后的 JSON 重新散列值混用。
