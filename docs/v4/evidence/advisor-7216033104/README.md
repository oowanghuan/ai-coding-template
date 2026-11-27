# Advisor 7216033104 修订证据

回应 [独立评审 7216033104](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7216033104)，原对象 `19cae4a43c00f3f224486fe1464a313146a5cba4`、Draft PR #5。两项均采纳，未扩大 WP-001/101 授权范围；本目录是作者复现/修订自测，独立复核仍待 #3 新结论。

## 实际复现与修复

旧代码仅增加两个回归用例，安装组 20 项中 1 失败、协议组 31 项中 1 失败，退出 1。`reproduction.json` 记录旧代码 SHA、修改文件和输入指纹，`reproduction.stdout/stderr` 保留实际失败输出。`reproduction-test_install.py.txt` / `reproduction-test_protocol.py.txt` 为与当次指纹一致的测试版本；复跑须在旧提交的隔离副本中恢复为对应 `tests/` 路径，不能拿修复后的代码冒充复现。

| 意见 | 旧行为与实际断言 | 修复及关闭条件 |
|---|---|---|
| WP-001 旧回执误删新补装 | A 安装；删除一个文件但保持 A 为 committed；B 补装相同内容；回退 A 错误返回 0 | 收据 v2 在写文件前保存重叠事务的先后证明。A 回退检测 B 的归属，退出 2，整棵文件树指纹不变。B 正常回退后，A 可正常回退，重复回退无变动。无先后证明的重叠旧收据、后继未知写入均保守停止 |
| WP-101 外部操作扩权保留旧签认 | 已验收快照仅增加 `external_effects` 并推进 revision；代码 SHA 不变；旧实现返回无错误 | 外部操作及其他签认输入统一纳入 `SIGNED_FIELDS`。扩大范围仍 accepted 被拒；显式失效旧签认并满足新授权后才可重开。撤销记录保留；从 invalidated 恢复 passed 必须使用新证据引用、追加新评审引用，不能重新挂回旧记录 |

修复代码实测提交：`ea89d0c91a48e71f600f6da2bcaae5a29104e1a9`。2026-11-27 10:43:33–10:44:04 UTC，macOS 15.5 arm64 / Python 3.9.6。安装 **23** 项、协议 **34** 项通过，失败/错误/跳过均 0，退出 0；原有正常/重复回退用例仍通过。详见 `results.json`、`tests.stdout/stderr`。

## 可直接核对的输入与输出

`external-effects-cases.json` 保存完整合成快照，以内容哈希索引；`transitions` 按实际执行顺序引用 before/after 与校验结果：

1. accepted → accepted，扩大范围但保留旧签认：`signature-invalidation-required`。
2. accepted → in_progress，显式撤销并登记新的范围授权：通过。
3. in_progress → submitted：通过。
4. submitted → in_review：通过。
5. in_review → accepted，重新使用旧证据/评审：三个 `fresh-signoff-required`。
6. 同一 in_review → accepted，改用新证据并追加新评审：通过，代码 SHA 仍与最初一致。

`installation-cases.json` 保存每次安装/回退的实际返回值、预期退出码、全树前后指纹及目标文件指纹。第 3 个操作是旧 A 回退：退出 2、changed_path_count=0；随后 B/A 的正常及重复回退均退出 0。

`capture_cases.py.txt` 是隔离运行的实际捕获驱动，包裹原测试中的校验/安装调用并保存其输入输出，没有替换产品返回结果。`cases.stdout/stderr` 是这 3 个已有用例的重复捕获执行记录，**不另算 3 个新增用例**。

沿用 [首批隔离策略及驱动](../first-batch/README.md)，沙盒指纹与驱动指纹记录于 `results.json`。运行前凭证环境剥离、目录外无敏感 canary 读写/仓库写入/联网拒绝五项检查均通过。128 个被测输入运行前后未变化。原始机器路径在公开记录中作替换，未改测试结果；公开文件指纹见 `sha256.json`。

## 本机接收与回复边界

`natural-detection.json`：10:40 的自然轮询读到 19 条评论，pending=1，准确识别本条 Advisor 评论及原受审 SHA；等待 Project Lead 核查，没有执行候选或自动扩大权限。

本次请复核的对象位于 `v4/first-batch`。为避免仍按 `v4/design` HEAD 校验而误拒或漏核对回复，受限 broker 新增显式 `expected_branch`，仅允许读取这两个已授权分支；旧 outbox 默认设计分支，main/未知分支拒绝。发评论前再次核对所选分支 HEAD。`poll.py.txt` / `test_poll.py.txt` 为实际源快照，`broker-tests.json` 记录 31 项隔离合成检查通过。写入仍只限 #3 评论，不执行模型、候选代码、Git 写入或 push。真实后台发布与下一轮去重以追加运行回执为准，不用合成测试代替。

未完成边界保持：真实授权/证据验真、原子认领与执行隔离引擎、跨供应商/多机恢复、Lite 用户路径及 S01–S12 产品端到端验收。收据关系依赖完整保留的本地历史，不抵御删改历史或不遵守协议的其他写者；签认校验验证声明关系，不证明新证据真实。
