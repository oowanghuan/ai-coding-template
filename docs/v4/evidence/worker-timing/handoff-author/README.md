# 停机前最终写入：作者回归证据

对应 Advisor 7236044988 的快照时序问题。本目录是实现作者执行的 `synthetic_fixture` 回归，`provider_live=false`，不构成独立签认。实际子进程由测试创建并登记 PID/进程组，以 stdin 指令控制其在快照后写文件并正常退出；没有调用模型或供应商登录。

## 修复前复现

[第一次结果](result-01.json)及[错误日志](stderr-01.log)保留真实失败：子进程在 checkpoint 后写入最终字节并 exit 0，随后 `confirm_stopped` 没有拒绝陈旧快照，测试期待的 ValueError 未发生。运行 1 项、失败 1 项、退出码 1，输入指纹不变。失败时未执行后续接管，不把尚未执行的断言计为实测；“接管丢失最后字节”的完整旧版本独立复现由非作者证据提供。

## 修复范围

`checked_checkpoint` 现在校对旧工作目录与已固定快照的路径、内容 SHA256、大小、执行位、目录集合以及 HEAD。复用有界 dirfd/no-follow 扫描，多次读取比较；不因进程已退出而接受链接或特殊文件。该检查覆盖停机确认、后续 claim、恢复开始前和恢复完成后。

不一致时保留原成果，拒绝停机确认或接管；恢复途中发现变化则保留已持久化的 `creating`，不发布 `prepared` 或允许提交。正向修复路径是实际旧进程停止后重新快照、重新确认，再恢复最终字节。

[完整接管回归结果](result-02.json)与[日志](stderr-02.log)：15 项全部通过，0 跳过，exit 0，203.538 秒。新增测试覆盖实际晚写后重新快照、停机确认后八类变更（内容、新增、删除、执行位、空目录、符号链接、硬链接、HEAD）、claim 后变更、恢复过程中变更。不把子测试变体另外累计为独立测试数量。

## 证据和运行边界

- 原始运行保留仓库外；[public-manifest.json](public-manifest.json)逐文件列出 original/public SHA256。公开副本替换本机路径，保留原始输入指纹；它们不是原始可信 receipt。
- [运行脚本文本](run.py.txt)与[沙盒配置](profile.sb)用于审查 A01 边界。候选只在外层 sandbox 运行，禁止网络、仓库写和其他进程信息读取，环境采用明确白名单。
- 复用的历史 harness 在结果 `note` 字段仍写有 “Non-author lifecycle/Store tests”；本次新增 handoff 修复及这些回归由同一作者执行，因此本目录统一标记作者证据，不据该历史字符串声称独立验收。
- `result-02` 的 before/after 覆盖并行开发中的多个输入，`source_unchanged=false`：仅并行额度修复的 `framework/local/lifecycle.py` 与 `tests/lifecycle/test_lifecycle.py` 发生变化，handoff 产品/测试保持不变。因此本次通过只能作为开发期回归；两项修复共同冻结后的精确版本复跑以独立证据为准。
- 权威锁只串行化状态操作，不是文件系统冻结。该协议依赖可信 supervisor 确认原进程组退出，并保持旧工作目录没有其他授权写者；检查拒绝观察到的迟到变化，不宣称抵御同账号宿主任意持续写入。Git 管理元数据依旧排除，但 HEAD 受核对。
- 原有 handoff 仅恢复文件字节及执行位，尚未完整恢复空目录拓扑。本次检测空目录迟到变更，不宣称修复该既有恢复边界。旧写者真实额度、供应商恢复和 hostile descendant 逃逸不由此合成夹具证明。
