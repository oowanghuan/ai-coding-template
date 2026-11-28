# 作者开发与测试证据

本目录保留 WP-301/302/303 的开发期运行记录，证据级别均为 `synthetic_fixture`（单元测试与固定合成 Worker 场景）。没有启动真实供应商模型，`provider_live=false`；不能据此宣称 Claude Code/Codex 的真实额度恢复、跨供应商原生 Session 恢复或正式工程验收完成。生命周期测试由非该产品实现作者编写，但仍使用合成可信观察，且恢复模块作者参与测试；最终独立复跑另见同级 `independent/`。

## 可追溯运行

| 记录 | 实际结果与范围 | 主要证据 |
| --- | --- | --- |
| Adapter 01 | 初版 35/35 通过，0 跳过 | [命令及输入](wp301-adapters-author/result-01.json)、[日志](wp301-adapters-author/stderr-01.log) |
| Adapter 03 | 扩充后 53/53 通过，0 跳过；5 项沙盒检查通过 | [命令及输入](wp301-adapters-author/result-03.json)、[日志](wp301-adapters-author/stderr-03.log)、[检查结果](wp301-adapters-author/stdout-03.log) |
| Recovery 01 / 03 | 初版 21/21；冻结恢复模块 26/26，均 0 跳过 | [初版](recovery-author/result-01.json)、[最终输入](recovery-author/result-03.json)、[最终日志](recovery-author/stderr-03.log) |
| Lifecycle 01 | 14 项夹具初始化错误：引用已不存在的 reviewer/acceptor；保留失败 | [结果](lifecycle-independent/result-01.json)、[错误日志](lifecycle-independent/stderr-01.log) |
| Lifecycle 03 | 18/18 通过，0 跳过，运行期间输入不变 | [结果](lifecycle-independent/result-03.json)、[日志](lifecycle-independent/stderr-03.log) |
| Lifecycle 04 | 27 项中 3 error；接管凭据解包导致 `baseline_sha` KeyError，且运行期间源码变化。仅诊断记录 | [结果](lifecycle-independent/result-04.json)、[错误日志](lifecycle-independent/stderr-04.log) |
| Handoff 05 | 修复后 9/9 通过，0 跳过，输入不变；包含实际子进程终止/wait/进程组消失检查 | [结果](lifecycle-independent/result-05.json)、[日志](lifecycle-independent/stderr-05.log)、[进程观察](lifecycle-independent/stdout-05.log) |
| Handoff 06 | 最后两项负测 2/2 通过，0 跳过，输入不变：未快照成果禁止接管，bool token/epoch 禁止冒充整数执行权 | [结果](lifecycle-independent/result-06.json)、[日志](lifecycle-independent/stderr-06.log) |
| Worker Demo 01 | 夹具角色引用错误，未完成 | [命令结果](wp303-worker-demo-author/result-01.json)、[错误](wp303-worker-demo-author/demo-01/demo-evidence/error.json) |
| Worker Demo 02 | 接管 `baseline_sha` KeyError，未完成 | [命令结果](wp303-worker-demo-author/result-02.json)、[错误](wp303-worker-demo-author/demo-02/demo-evidence/error.json) |
| Worker Demo 03 | 固定合成进程闭环完成，exit 0；旧写者退出、快照接管、旧 token/重复交付拒绝、原 Worker 回池；工程验收仍为 false | [命令及指纹](wp303-worker-demo-author/result-03.json)、[摘要](wp303-worker-demo-author/demo-03/demo-evidence/summary.json)、[操作流水](wp303-worker-demo-author/demo-03/demo-evidence/journal.json) |
| Demo 单元测试 | 2/2 通过，0 跳过，输入不变 | [输入结果](wp303-worker-demo-author/tests-result.json)、[日志](wp303-worker-demo-author/tests-stderr.log) |

上述运行属于多个开发快照，不能相加当成一次最终版本验收。Demo 03、Lifecycle 03/05 早于最后 `handoff_required` 等修复，具体版本以每个结果的 before/after 指纹为准；最终状态的复跑由总证据索引说明。通过但冗余的中间 Adapter 02（52 项）、Recovery 02（25 项）、Lifecycle 02（14 项且源码变化）不在此重复复制，原件仍留仓库外。

## 边界与复核方式

- 候选代码仅在 A01 外层 macOS sandbox 执行；保留[外层配置](harness/quality-governance-regression-02/sandbox.sb)、[配置参数](harness/quality-governance-regression-02/config.json)及各测试调度脚本文本。脱敏后的脚本/路径是审查资料，不是可直接运行的凭据或配置。
- 5 项检查是受保护文件读/写、仓库写、网络连接拒绝，以及敏感环境变量缺席。后者本身不证明所有凭据隔离；profile 另限制其他进程信息读取和 Keychain，未扩大为万能沙盒安全证明。
- 合成进程实际运行与文件/Git/权威状态操作是真实本地执行；“额度耗尽/恢复”等来源是明确测试夹具，没有供应商真实额度事件。并行观察不代表真实模型并行开发；进程组测试不覆盖所有恶意后代/逃逸场景。
- Demo 03 保留[快照清单](wp303-worker-demo-author/demo-03/demo-evidence/checkpoint-manifest.json)、[最终状态](wp303-worker-demo-author/demo-03/demo-evidence/final-state.json)及 `*.ready.log`、`*.finished.log`、`*.stderr.log` 原日志的脱敏副本；不复制全量 Git/workspace 或任何私有项目账本。
- [public-manifest.json](public-manifest.json) 逐文件列出仓库外原始 SHA256 与公开副本 SHA256。替换仅涉及机器路径和合成 Session 标识；嵌入的历史哈希保留原值，不能拿公开副本冒充原始可信 receipt，也不能要求脱敏后的嵌入指纹仍对修改后的内容成立。所有当前副本可按 `public_sha256` 独立核验。
- 本目录不含供应商 CLI 登录/doctor 原始输出、真实账号会话或认证信息。三条合成 Session 标识已一致替换为 `fixture-context-N`，保留对应关系。
