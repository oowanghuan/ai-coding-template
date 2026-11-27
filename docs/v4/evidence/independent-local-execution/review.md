# WP-102/103 非作者验证公开证据草案

受审提交：`ed1bbd8b36df42c8a6ec0ea1f0c44ea52fee3ed6`。实现与回归代码提交：`984eb6993ac1f3cb06d652f448c0680845b1bf65`。

这份材料整理已有实测记录；整理期间没有重新执行候选、修改实现或启动 Docker。执行者未编写本次候选实现，使用独立执行上下文，但仍在同一物理主机、同一 OS 账号。它提供非作者复跑证据，不等同于外部隔离主机认证、Owner 工程验收或产品验收。

## 实测结果

| 测试组 | 执行 | 通过 | 失败/错误 | 跳过 |
| --- | ---: | ---: | ---: | ---: |
| install | 23 | 23 | 0 | 0 |
| protocol | 34 | 34 | 0 | 0 |
| local | 26 | 23 | 0 | 3 |
| bootstrap | 19 | 19 | 0 | 0 |
| 合计 | 102 | 99 | 0 | 3 |
| 额外非作者探针 | 4 | 4 | 0 | 0 |

完整回归：2026-11-27 15:20:08–15:22:02 UTC，退出 0。额外探针：15:21:22–15:21:37 UTC，退出 0。两批读取的候选输入指纹执行前后均相同。统计、时间、脱敏调用和输入指纹分别见 [counts.json](counts.json)、[probes.json](probes.json)、[candidate-inputs.json](candidate-inputs.json)。原始测试输出以无改动、经公开性检查的日志副本保留：`regression.*.log`、`probes.*.log`。

候选导入与子进程执行均处于实际外层沙盒内；隔离探针验证外部文件读取、外部写入、checkout 写入、网络连接被拒，凭证环境已移除。没有取消外层保护来消除跳过。机器专用权限配置、用户路径、内部执行上下文标识与原始私有运行目录不公开。

## 已复核整改与四项补充探针

两项已有整改在本次执行中未复现原缺陷：失败运行回放保持非零并保留原结果，不重复启动；安装初始日志写入后、独立收据产生前硬崩溃，可由新进程公开 rollback CLI 中止，未知文件仍被保护。成功 receipt 回放用例使用合成 receipt，只证明回放语义，不视为真实 Runner 成功链。

额外四项探针分别记录：

1. 8 个真实进程同时基于同一 revision 认领，仅 1 成功，7 个 revision conflict；最终 1 个 assignment、revision=1。
2. lease 精确到期后重新认领，token 由 1 增至 2；新进程持旧凭据 heartbeat 被拒，authority 字节不变。
3. upgrade 写 preparing journal 后硬退出 23，尚无 receipt；新进程 rollback 退出 0，旧 selection 恢复、state 保持，再次升级成功。
4. schema 合法、assignment 已 revoked、workspace 仍 creating 时，升级被 unknown execution 分支拒绝，inventory 不变。

四项断言的脱敏源码见 [independent-probes.py.txt](independent-probes.py.txt)。仅将本机 checkout 路径替换为 `<REPO>`，没有改动执行语句或断言；该审阅副本不能原样运行，复跑须先落实隔离、依赖及路径。源码中的 `session-a` / `worker-a` 为合成测试夹具值，不是实际会话或设备标识。原始源码 SHA-256：`735cc77fe9bfff9d35edc96c7b7eeb08fa7c2696b62538af44506d61bff5208d`；公开副本 SHA-256：`fd521794f28eb510b37ab56145bfd4d003b5dd38abfde236bdf769b2f79c9e4c`。两者对照亦记录在 `probes.json` 与哈希索引中。

第 4 项补足现有 `test_unknown_execution_blocks_upgrade` 的证据弱点：原用例构造不完整 workspace，并允许以 invalid local state 拒绝，单凭原用例不能证明 unknown-workspace 分支。建议后续把合法 fixture 纳入持久回归；本次没有修改受审代码。

## Runner 证据边界

三项跳过分别是完整 Runner 单任务、完整 Runner 双任务、内层生产策略隔离探针。另一次只执行系统 `/usr/bin/true` 的最小复现，在 2026-11-27 15:18:54 UTC 得到：单层 Seatbelt 退出 0；嵌套 Seatbelt 退出 71，错误为 `sandbox-exec: sandbox_apply: Operation not permitted`。具体命令和日志指纹见 [nested-seatbelt.json](nested-seatbelt.json) 与 `single.*.log` / `nested.*.log`。这项复现没有执行候选，只证明该主机的实际嵌套断点。

继承外层隔离的两个真实 Worker、Worktree 与交付捕获组件已有通过记录，但没有经过产品 `run()` 的完整内层启动链。单独 Worker 策略探针和失败关闭测试同样不能替代成功链。不得把三个 skipped 改记为 pass。

独立发现 **RVI-01**：受审树 `tests/local/test_local.py:320` 的 `test_two_isolated_workers_execute_concurrently` 检查两次 run 结果和不同 PID，但没有断言真实 Worker 执行区间重叠，也没有为两个 Worker 分别提交捕获 delivery。这是验收覆盖缺口，不是已观察到的运行失败。后续应记录真实开始/结束或同步握手证据，验证重叠，再分别以新鲜凭据捕获两份成果、核对指纹与 `accepted=false`。当前受审代码保持不变。

可信外部驱动器、一次性文件信箱和独立 Worker 沙盒目前仅有技术提案，尚未实现或验收。若采用，必须作为明确的新 external-launch 后端，审查固定命令/策略、submit/status/cancel、幂等及未知结果处理；它不能冒充现有 direct 后端证据。没有因该提案启动额外服务或绕过 A01。

真实断电、未知进程自动接管、跨机时钟漂移、真实供应商集成和完整 Lite 用户路径未由本材料验证。没有把独立技术复核、提交或规范签认称作工程/业务验收。

## 可核验性与脱敏

`artifact-index.json` 保存本目录公开文件 SHA-256，并注明原始来源记录的指纹。JSON 中的 `<ISOLATED_RUN>`、`<SYSTEM_PROBE>` 是路径占位符；脱敏命令不能原样执行。来源元数据与公开副本指纹分别标记，不能混用。原始记录保存在仓库外，未被本次整理覆盖。哈希只能帮助比对内容，不能单独证明执行者身份或结果真实性。
