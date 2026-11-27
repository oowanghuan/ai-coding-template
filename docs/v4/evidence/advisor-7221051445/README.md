# Advisor 7221051445 两项整改

意见：[7221051445](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7221051445)，原受审版本 `66603e1030d17a45dd2e8f477b0c1457f55e12e3`。修订实测代码：`984eb6993ac1f3cb06d652f448c0680845b1bf65`。随后仅追加本证据目录。状态为已修订、待独立复核，未自行关闭 Advisor 意见或工程验收。

## 原版复现与修订

先给原版实现加入四个新回归，未改实现，隔离运行得到 2 failure / 0 error / 0 skipped：

1. 实际内层 Seatbelt 启动失败，保存进程退出码 71。首次 CLI 非零，同 ID 重试却退出 0 并输出 exit_code=71，确认误报成功。
2. 新进程在 preparing 日志原子写入后、事务收据写入前 `os._exit(23)`；另一进程调用公开 rollback CLI，原版返回 unknown installation，确认无恢复入口。

`before.stdout.log` / `before.stderr.log` 保留上述失败。复跑原缺陷可在原受审实现上使用修订提交中的两个测试文件及 `focused-harness.py.txt`；四个回归的原实现结果为 2 失败、2 通过。所有候选仍须在外层隔离中执行。

修订行为：

- finished 回放检查原退出码；失败仍向 CLI 返回失败，不启动新进程、不增加交付。原 PID、退出码、日志指纹和字节保持。成功 receipt 可正常回放；该成功回放用例使用显式合成的已提交结果，不冒充真实 Runner 成功链。
- 第一份安装日志包含零写入 receipt intent。收据缺失时，公开 `rollback --operation-id` 验证该意图并沿用原回退预检；任何已存在的拟创建文件仍视为未知写入而拒绝，不凭相同字节推断所有权。成功中止后可重新 plan-import/apply。旧日志缺少可验证意图时保留现场，不补造历史。

`focused-after.*.log`：四项均通过。新进程恢复用例确认原用户文件保留，恢复后可重新接入；负例确认未知文件和目录指纹完全不变。`journal_saved` 是新增可注入断点，回归还用包裹原子写入并硬退出的独立方式触发，不只依赖该 hook。

## 固定 SHA 全量回归

| 组 | 执行数（含 skipped） | passed | failure/error | skipped |
|---|---:|---:|---:|---:|
| install | 23 | 23 | 0 | 0 |
| protocol | 34 | 34 | 0 | 0 |
| local | 26 | 23 | 0 | 3 |
| bootstrap | 19 | 19 | 0 | 0 |
| 总计 | 102 | 99 | 0 | 3 |

`test-result.json` 记录准确 SHA、命令、时间、平台、源文件指纹、退出码 0，以及执行前后 unchanged=true。`tests.stdout.log` 和 `tests.stderr.log` 是输出副本。使用此前已审查的外层 Seatbelt 策略和 harness（位于 `../local-execution/`）；无网络、无发布凭证、checkout 只读，只有一次性夹具可写，5 项外层隔离探针通过。

原有三项 skipped 保持，不作通过声明。完整生产 Runner 单/双任务成功链仍未验证；独立非作者关键故障复跑仍未完成。此前单独 Worker 沙盒记录是原提交的组件证据，不能扩成此次完整链路验收。没有取消 A01 保护，没有增加费用或启动模型。

## 本次为何再次停工

`poll-20261127T144005722034Z.json` 与 `poll-20261127T145505828576Z.json` 显示：14:40 已读到新意见，14:55 仍 30 comments / pending=1 / processed=0，等待 Project Lead 调查。既有会话投递消费者仍未接通，本次再次由 Owner 追问使当前会话接手。不能将此停工归因于等待 Owner 批准，普通整改已有 OD-07 授权。

产品目标、关键路径、当前验收条件及阻塞责任已整理到 `V4_WORK_PACKAGES.md` 首页，覆盖过期的“未授权下一批”等说明。自动投递继续单独标为未完成，不承诺结束当前会话后会自动开展研发。

## 公开处理

仅替换绝对 workspace、依赖、夹具和无害 canary 路径；原始日志留在仓库外。`artifact-index.json` 记录原始/公开字节指纹。两份轮询记录仅取公开项目运行摘要，未提交原始输入、凭证、私有项目或客户资料。
