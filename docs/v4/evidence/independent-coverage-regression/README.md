# 独立复跑：补强测试后的准确提交

受审 SHA：`0ef5434bb71d714ae1068c31786fbb8058cb050c`。产品实现仍为 `984eb6993ac1f3cb06d652f448c0680845b1bf65`；本次提交只补强两个测试文件。

非作者复核者在独立执行上下文完成一次全量复跑，同一物理主机、同一 OS 账号。没有修改实现、仓库测试或发布；不代替 Owner 验收。

实际结果：**103 执行，100 通过，3 跳过，0 失败，0 错误，进程退出码 0**。5 项外层隔离探针通过。

| 测试组 | 执行 | 通过 | 跳过 | 失败/错误 |
|---|---:|---:|---:|---:|
| install | 23 | 23 | 0 | 0/0 |
| protocol | 34 | 34 | 0 | 0/0 |
| local | 26 | 23 | 3 | 0/0 |
| bootstrap | 20 | 20 | 0 | 0/0 |

`test-result.json` 保存命令、显式环境、开始/结束时间、退出码和执行前后源码指纹，unchanged=true。`commit-input-verification.json` 核对 181 个受测输入文件，均与上述准确提交一致；包括模板、示例、manifest、旧工具定义，防止只校验 Python 文件而漏掉测试输入。启动时仅工作包文档有未提交整理，不参与候选执行。

`tests.stdout.log` / `tests.stderr.log` 为实际执行输出。`artifact-index.json` 记录原始与公开副本指纹。仅脱敏绝对 workspace、依赖、夹具和无害 canary 路径，原始记录保留在仓库外。

## 本次新增覆盖的结论

合法 unknown-workspace 用例经实际 claim → start → revoke 状态转换，显式通过 shape 校验并断言 revoked + creating，随后精确验证未知执行阻止升级、inventory 不变。原非法状态检查另行保留，不再混为同一证据。

双 Runner 用例静态复核确认增加了不同目录、退出码、受控交付身份/epoch/token/路径/基线/指纹/实际字节及主目录保持断言；本次仍因 nested Seatbelt 跳过，**这些新增成功链断言尚未执行**。测试已改名为 distinct deliveries，不以线程并发或 PID 不同宣称 Worker 执行时间重叠。

两个 Advisor 修订回归均再次执行通过：失败 CLI 回放保持失败及原状态/日志；安装 journal 与 receipt 之间硬崩溃可由新进程公开 rollback CLI 恢复，未知文件负例仍保护现场。

## 边界

全部候选执行均通过既有外层 Seatbelt、系统 Python `-B -S` 与显式白名单环境；无网络、无发布凭证、checkout 只读。没有禁用外层保护、调用模型或引入费用。

3 项跳过为生产 Runner 单任务成功链、双 Runner 捕获交付链和内层策略探针。继承外层隔离的实际 Worker 组件运行不能替代完整生产 Runner。未知进程接管、完整供应商集成及 Worker 时间重叠均不据此宣称完成。

本轮没有重跑此前额外 4 个独立探针，也没有把此前结果计入本轮数字。结论支持当前已实测范围的独立技术复核，整体 WP 工程验收仍保留未验证项。
