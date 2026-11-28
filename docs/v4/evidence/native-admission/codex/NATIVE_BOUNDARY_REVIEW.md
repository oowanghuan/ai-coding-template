# WP301：原生执行准入有界复核

结论：**当前已测 Codex 0.169.0 本机原生执行配置仍不准入 live；本条有限调查已完成。** 本轮没有新建或恢复模型会话、推理请求、产品修改或权限放宽。静态工具面核查没有证明一个可直接投产的 text-only 全闭合入口。不能把关闭 shell、只读文件权限、审批 never 或提示词当成全面隔离。

## 实测与静态证据分开

- 本轮安装版只读元数据：版本 `codex-cli 0.169.0`；binary SHA256 `739cda86e15d30a6e2b40cf8dcbbfb988aaf48b305b27065573bb8e9fd41d002`。version、sandbox --help、exec --help 均 exit 0，模型调用 0。
- `codex sandbox macos --help` 在此安装版被当作执行 literal macos，exit 71、execvp 找不到该程序；保留原失败，不计成功 help。当前公开手册例子仍与本机 flat `sandbox` 接口不同，应以实际 help 为执行依据。
- 沿用此前真实固定系统探针：named profile 下文件/网络限制不等于阻止进程环境读取，读取另一个自有合成进程的 KERN_PROCARGS2 成功；外层 deny process-info others 与原生内层 Seatbelt 叠加在 sandbox_apply 阶段 exit 71。此轮没有重跑相同失败配置，也没有无沙盒 fallback。
- 本轮官方 Claude 2.1.332 的只读 auth help 确认 status 合法后，在既有 safe/restricted/setting-sources 清白环境边界下重查：exit 1、loggedIn false。仅代表该准确调用环境，不推断账户没有订阅或任何其他入口都无授权。原始 auth stdout 不进入公开材料。
- 官方精确 tag rust-v0.169.0 的 permissions profile 字段覆盖 filesystem/network，没有在本次读取的字段和 sandbox CLI 参数中找到 process-info deny/custom SBPL 接口。sandbox-state JSON 由固定类型解析；External 转成本地 read_only，并非任意政策注入。
- 源码 tag 名与安装版 version 一致不是二进制构建溯源证明。official-source-index.json 的 SHA 绑定本地保存文本副本（工具文本保存可能含额外末尾换行），不是 Git blob ID 或已安装 binary 的源码证明。

## shell_tool=false 后的注册面

本表穷举本次读取的 core spec_plan 注册类别；并不穷举插件/远端服务当前实际工具目录。独立 handler 复核见后附报告。具体 CLI 配置到内部值的最终生效，以及 managed 层覆盖，未通过新会话观测。

| 类别 | 准确 tag 的注册条件/控制 | 关闭 shell 后的结论 |
|---|---|---|
| ExecCommand / WriteStdin | Feature::ShellTool 为 false 则 add_shell_tools 返回；UnifiedExec=false 会改注册 one-shot ExecCommand | 前者可静态移除此处命令工具；后者不是禁命令 |
| ApplyPatch | model_info.apply_patch_tool_type 存在；该分支无 shell 开关、未见独立禁用 feature | 可能保留写文件能力；不存在“禁 shell 就禁 patch”的结论 |
| ViewImage | Feature::ViewImage | 独立可控注册；实际有效关闭未验 |
| MCP 资源 list/templates/read | 有 servers 或 CodeModeOnly | 仍可能保留外部资源读取；不是普通 shell |
| MCP tools / apps | MCP binding/catalog、apps_enabled、config 与各服务策略 | 独立加载；未读取本机私密配置，不掌握有效工具全集 |
| extension tools | 逐个注册；web/run 另外看 search 开关，imagegen 看 ImageGeneration/模型/provider/auth 条件 | 未见一个 shell 总开关覆盖其他 extension；实际加载集合未知 |
| dynamic tools | 调用方传入的每个函数/namespace 外部注册 | 空列表只关闭这一路，不能证明其他工具已关 |
| hosted/native web search | web_search_mode、模型能力和搜索路由 | 独立于 shell；需单独验证 disabled 及服务工具 |
| collaboration | MultiAgentVersion Disabled 关闭；V1 看深度；V2 看 disable_native_tools 等 | 不受 shell 总开关；V2 direct-message=false 仍不等于整个协作关闭 |
| plugin suggestion/install | ToolSuggest && Apps && Plugins 且存在候选 | 可能改变可用集；需独立关闭和确认 |
| permissions request | RequestPermissionsTool | 需独立确认；审批策略不是能力移除 |
| plan / deferred environment / user input & async message | 各配置、feature、model capability | 不因 shell=false 自动移除 |
| context/window / time / sleep / test_sync | 各 feature 或模型宣告 | 仍有独立注册分支 |
| tool search / code-mode | registry 暴露与包装层 | 改显示/包装方式不是取消底层能力 |
| 同名 read_file/list_dir | core 注册中未见同名模型 handler；exec-server 有文件系统能力 | 只能说当前读取范围未见独立注册，不能说整个产品不会读文件 |
| 启动配置、rules/skills/hooks、managed 行为、会话恢复上下文 | 不属于该注册函数的完整审计面 | 仍未形成准确生效闭包，不能以本表宣称 text-only |

内部 registry 确有 session ToolPolicy；此次未建立一个对本机安装版可验证、覆盖所有上述面且无需新会话的公开全局 allowlist 配置。这里是“未证明可用”，不是断言任何版本都不存在。

handler 独立检查的有限结论：view_image 把 sandbox_context 传给 metadata/read_file，并对读回字节做图像解码，不能描述为任意文本读取工具；apply_patch 经过 sandbox/effective filesystem/write/approval 路径而不依赖 shell 注册。LocalFileSystem 按策略选择 sandbox helper 或直接 FS，传入 Some(context) 本身不构成 A01 强隔离证明。当前尚无本机准确 effective toolset 取证。

## 可执行的解除条件与下一步

1. **命令执行路线**：先获得当前官方支持、可在同一有效隔离层阻止其他进程信息读取的实际接口/环境变化。再提交固定 owned-process marker 探针的精确脚本/policy/hash，非作者审核后仅重跑该有限系统探针。必须同时证明 marker 不可见、外部文件/凭证/网络与权限边界不退化。无变化时不重跑，不等待模型“自觉”。
2. **text-only 候选路线**：先建立精确安装版可复核的生效配置闭包和工具目录：shell、patch、image/file、MCP/apps、extensions/dynamic、search、collaboration、plugin、hooks/skills/rules/managed 行为。所有可能触及宿主或外部服务的入口应有支持的禁用/隔离机制；独立审查验证遗漏默认拒绝。若工具全集只能启动新会话才能证明，本轮约束下该项保持 unknown，不能偷启会话补证。
3. **认证是另一个独立前提**：在最终批准的相同环境内，官方只读 status 应能确认可用认证；本次 Claude false 尚不满足。不得为通过检查复制个人 token、换到宽松环境或自动 login。
4. 上述安全前提成立后，root 再安排有限无新费用的真实供应商验收；本轮没有 provider_live 证据，也没有检查额度的实际模型请求。真实会话/费用/新基础设施不在本次已执行内容中。
5. 本机原生准入 blocked 不影响 synthetic 生命周期、恢复、固定 document Gate 等已完成产品路径；不得将它们冒称两家 CLI 的 live 验收。

## 仓外原件与公开范围

- 同目录 metadata.json、各 help/version stdout/stderr、official-source-index.json 保存安装元数据与来源摘要。
- Claude 状态安全摘要位于独立 auth metadata 目录 status-summary.json；原始私有 stdout 只保留仓外。
- 本报告不包含账户邮箱、token、会话 ID、私有仓库材料或个人绝对 home 路径。
- root 负责公开脱敏、历史真实探针的既有证据引用以及协作台账状态；不复制官方整份源文件或原始 auth stdout。

## 官方来源

- [准确 tag 工具注册](https://github.com/openai/codex/blob/rust-v0.169.0/codex-rs/core/src/tools/spec_plan.rs)：本表注册类别与条件。
- [准确 tag 权限字段](https://github.com/openai/codex/blob/rust-v0.169.0/codex-rs/config/src/permissions_toml.rs)：profile 配置形状。
- [准确 tag sandbox CLI](https://github.com/openai/codex/blob/rust-v0.169.0/codex-rs/cli/src/debug_sandbox.rs)：SandboxState 解析和 External 转换。
- [准确 tag Seatbelt base](https://github.com/openai/codex/blob/rust-v0.169.0/codex-rs/sandboxing/src/seatbelt_base_policy.sbpl)：same-sandbox process-info allow。
- [官方 permissions](https://learn.chatgpt.com/docs/permissions)：filesystem/network profile 与其他工具/服务流量边界。

