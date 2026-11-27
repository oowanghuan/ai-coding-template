# V3 能力盘点与验证记录

基线：`8ed245f5a5c7adeebd31b3f31272164ee85a1d39`。盘点日期：2026-11-26。
结论级别分为 **仓库事实 / 隔离实测 / 设计判断 / 未验证**，不得混用。

## 1. 仓库事实与保护措施

启动目录为空，随后从 `oowanghuan/ai-coding-template` 克隆。远端默认分支 main，仓库公开。克隆后及后续只读核查的远端 main 均为上述 SHA；与用户给出的审查基线没有变化。

先建立本地 `v4/discovery-design`，Owner 指定发布分支后建立 `v4/design`，保留全部未提交成果。切换时 HEAD 仍为基线，`origin/main...HEAD` 为 `0 0`；未提交内容仅新增 `docs/v4/` 和 `tests/`。未执行旧初始化文档中的删除 `.git`，未修改、删除或覆盖任何旧版跟踪文件。

关键时间证据与命令见 [Git 核查记录](evidence/git-baseline.txt)。本轮提交历史应只包含公开基线之后的第一轮新增交付，不携带其他仓库历史。

## 2. 阅读与审计覆盖

| 范围 | 文件数 | 方法 |
|---|---:|---|
| README、CLAUDE_INIT、CHANGELOG、AUDIT_REPORT、AUDIT_RESPONSE | 5 | 主文档阅读；旧审计与当前内容交叉核对 |
| `_project_context/` | 3 | 原则、协作和角色模型阅读 |
| `01_workflow/` | 11 | 流程、PM Driver、恢复、并行开发及日常操作核对 |
| `03_templates/` | 38 | 全量文件清单；模板结构、字段、依赖和关键 Gate 深读 |
| `05_tools/` | 41 | 全量源文件对照、入口/依赖扫描，关键命令深读 |
| `07_phase_gate/`、`08_legacy_integration/` | 2 | Gate、现有项目接入和契约解析阅读 |
| `.claude/` | 55 | 与源文件逐字节对照，差异和仅安装目录存在的能力检查；Hook 实测 |
| `scripts/` | 1 | 安装脚本全文检查及隔离执行 |
| 合计 | **156** | [逐文件路径、行数、字节数与 SHA256](evidence/p0/source-manifest.json) |

补充检查 `_gui_config/README.md`、Git 跟踪文件及 `_backup` 体积。对完全相同的工具副本采用哈希等值核对，差异文件单独查看 diff。覆盖表区分全文/结构/关键机制阅读，不把文件哈希清单称为全部示例的逐行语义验证；长篇模板中的全部示例尚未逐个执行验证。第一轮发现也不等于对整仓所有历史内容的完整独立审计。

用户授权的私有实践入口、角色/规范/偏离资料、工作看板与决定记录、进度报告、指导意见及历史讨论已通过只读方式研究；评审目录列举后抽样读取锁定清单、索引及工程复核记录，没有运行其中代码。原始资料和阅读记录保存在仓库外。本公开盘点不附私有名称、链接、工作包、业务规范或完整评审记录；通用设计要求可以从本项目公开材料和任务目标独立理解。

## 3. 旧框架能力地图

“原样复用”指指定资产或机制，不承诺旧版整个执行链可直接运行。

| 能力 | 已有事实与仓库证据 | V4 判定 | 原因与边界 |
|---|---|---|---|
| Phase 0–7 工作流 | [README §5](../../README.md)、[框架概览](../../CC_COLLABORATION/01_workflow/02_FRAMEWORK_OVERVIEW.md)；Foundation/Kickoff/Spec/Demo/Design/Code/Test/Deploy，已有可裁剪思想及需求起源层 | **修改后复用** | 保留工作方法和编号映射；按 WP 类型选择必要里程碑，不将 Phase 等同产品状态 |
| Foundation Gate | [00_FOUNDATION_GATE.md](../../CC_COLLABORATION/03_templates/00_foundation/00_FOUNDATION_GATE.md)：MVS、用户流程责任、模块映射、冻结与重新审批 | **抽象为供应商无关协议** | 保留开工前定义目标/架构/依赖的原则，Lite 用最小 MVS；身份、授权、版本校验须可执行 |
| Project PM Driver | [project-pm.md](../../CC_COLLABORATION/05_tools/slash-commands/project-pm.md)：init/ready/assign/check/sync/logs；assign 输出 CLI 命令 | **重新实现执行部分，复用规则素材** | 目前主要是 Prompt 规格与 Human 分发；没有原子认领、统一 Worker Pool 和实际调度进程 |
| Feature AI PM Driver | [ai-pm.md](../../CC_COLLABORATION/05_tools/slash-commands/ai-pm.md)、[ai_pm_state_manager](../../CC_COLLABORATION/05_tools/skills/ai_pm_state_manager.md)：intent/policy/runtime、重试、熔断；明确编排不存执行事实 | **抽象为供应商无关协议** | 编排与事实分离值得保留；迁移为有测试的状态机，不复制整份 Prompt 到 Codex |
| Ready Set / 依赖 | [PROJECT_TRACKER_TEMPLATE.yaml](../../CC_COLLABORATION/03_templates/00_foundation/PROJECT_TRACKER_TEMPLATE.yaml)、project-pm:305–335 | **修改后复用** | 已判断依赖与目录；需要增加授权、里程碑版本、有效认领、能力和作用域冲突 |
| Phase Gate | [PHASE_GATE_TEMPLATE.yaml](../../CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml)、[gate_checker.md](../../.claude/skills/gate_checker.md) | **重新实现执行内核** | 规则/状态分离及检查分类可继承；现有多数内容是模型执行指南，缺可信取证链和强制真实测试 |
| Expert Review | [expert-review.md](../../CC_COLLABORATION/05_tools/slash-commands/expert-review.md)、[REVIEW_ACTIONS_TEMPLATE.yaml](../../CC_COLLABORATION/03_templates/_shared/REVIEW_ACTIONS_TEMPLATE.yaml) | **抽象为供应商无关协议** | 保留问题、证据、影响、修复、责任字段及 GO/REVISE/BLOCK；不固定 OpenAI API 或把不同模型当独立身份 |
| Contract Resolver | [.claude/skills/contract_resolver.md](../../.claude/skills/contract_resolver.md)：实体/端点输入、来源文件/行号、真实字段、Mock 核对、置信度 | **修改后复用** | 这是有价值的仅安装目录资产；增加权威登记、精确版本与多契约冲突报告，置信度不能替代验收 |
| Progress Log | [90_PROGRESS_LOG_TEMPLATE.yaml](../../CC_COLLABORATION/03_templates/_shared/90_PROGRESS_LOG_TEMPLATE.yaml)；meta、阶段任务、stats、cc_checkpoint | **抽象为供应商无关协议** | 继承持久化进度，明确主状态与派生报表；不从任务 done 或百分比推断业务成功 |
| Context Recovery / iresume | [CONTEXT_RECOVERY.md](../../CC_COLLABORATION/01_workflow/recipes/CONTEXT_RECOVERY.md)、[iresume.md](../../CC_COLLABORATION/05_tools/slash-commands/iresume.md) | **修改后复用** | Recipe 已要求 Git status/diff 和工作中保存，不能说旧版没有恢复；需补租约、未追踪成果、未知操作和跨供应商交接 |
| Commands/Skills/Subagents | [工具目录](../../CC_COLLABORATION/05_tools/README.md)、`.claude/` | **抽象协议并重新生成适配入口** | 五个命令漂移、15 个仅安装 Skills，当前原生格式需更新；源规则单份，包装派生 |
| HA Loop Desk | [GUI 配置说明](../../CC_COLLABORATION/_gui_config/README.md)、[Hook](../../.claude/hooks/check-gui-cmd.py)、GUI 三命令 | **保留 V3；V4 修改后兼容只读视图** | 已声明 configLoader/template-scanner 路径依赖；receipt ACK 不是完成回执。不跨仓修改 GUI，不承诺当前 GUI 理解 V4 |
| 现有项目接入 / 逆向 | [接入指南](../../CC_COLLABORATION/08_legacy_integration/README.md)、integrate-project/scan-project/reverse-api/reverse-schema | **修改后复用** | 保留 Level 0–3 渐进接入及 legacy/逆向/推断/已验证标记；去掉“接入即追溯通过”的验收捷径 |
| 规划/Context/设计/测试/发布模板 | [03_templates](../../CC_COLLABORATION/03_templates/README.md)，含正反场景、风险、回退及 ADR 素材 | **原样保留内容素材，按需修改字段** | 不强迫搬家；业务项目可直接选用内容结构，先修路径和字段引用，再增加 V4 元数据 |
| Git Commit 规范 | [04_REFERENCE 附录 A](../../CC_COLLABORATION/01_workflow/04_REFERENCE.md) | **原样复用** | Conventional Commits 与供应商无关；移除具体流程中的默认 main 推送假设 |
| 旧 GUI 工程与截图 | `_backup/`：228 个跟踪文件，20,950,550 字节 | **归档保留；从新模板发布清单排除** | 保护历史，避免新项目携带废弃 GUI；本轮不删除或重写历史 |

## 4. 外部静态发现的重新核实

| ID | 严重性 | 当前结论 | 证据与后续 |
|---|---|---|---|
| F01 | 高 | **确认：五个同名命令字节和语义漂移** | ai-pm 缺项目活动日志；check-gate 仍调用 gate_checker；check-progress 阶段旧名；daily-summary 旧 `_system` 路径；new-feature 安装副本不生成 Gate。`results.json.drift.commands` |
| F02 | 高 | **确认：源 6 个 Skills，安装 21 个，额外 15 个不能全删** | contract_resolver、api/schema/module/tech_stack scanners 是接入功能依赖；其余仍被命令/Subagent 引用。源 5 个 Subagents 与安装副本等值；只改 README 不等于断链全部修好 |
| F03 | 高 | **已复现安装失败** | R01：退出 1，源目录 `_templates/CC_COLLABORATION/05_TOOLS` 不存在。正确目录是 `CC_COLLABORATION/05_tools` |
| F04 | 高 | **确认默认构建/测试未启用；未复现完整模型伪报过门** | Gate 的 exec_check/test_check/e2e_check 都在注释中；Demo 的 serve_check 是活动规则，不能说完全没有执行检查。CHANGELOG v3.2.0 记载历史伪报，但历史事件非本轮实测 |
| F05 | 高 | **确认协议缺口** | 现有指令/状态以 Claude Session 与 Feature 为核心，未形成跨 Provider 的 Assignment、fencing、Evidence 身份链。属于范围审计，不是运行故障 |
| F06 | 中 | **确认历史资产占比与目录存在** | results.json 的 backup 数量/字节数；未运行 `_backup` 中 GUI 测试，不能当模板 CI |
| F07 | 高 | **确认分发以人工为主** | project-pm assign 指导打开多个 CLI、复制命令。R09/R12 只测试文档算法，未启动真实多 Agent |
| F08 | 高 | **确认缺少模板自身一致性测试入口** | 基线无根级 tests/、schemas/、.github 工作流；`_backup` 有 GUI 测试，不覆盖安装/命令/模板一致性。新 P0 脚本是观察基线，不冒充 V4 门禁 |

### 新发现与未被证实的疑点

- **F09**：工具源有 26 个命令，安装副本只有 25 个，缺 `/project-pm`；README/Skills 文档的计数仍有 24/5 等旧值。不能靠修帮助文案解决工具闭包。
- **F10**：R02 `--list` 输出三个缺失目录错误但退出 0，自动化可能误判成功；R03 不支持 `--dry-run`。
- **F11**：R05 路径修正副本安装 37 个文件，但不安装 settings.json/hooks；与 CLAUDE_INIT 的承诺不符。R08 证明已有文件被跳过并保全，不覆盖是优点，但无法自动更新漂移副本。
- **F12**：`new-feature` 源引用不存在的 `_shared/DOC_CHANGELOG.md`；`expert-review` 指向不存在的 `_common/REVIEW_*`；`doc-design-validation` 仍用不带 `_planning` 的路径；`/init-gate` 被引用但没有定义。这些是当前静态断链，需 WP-001 建立统一 manifest。
- **F13**：Ready Set 示例混用 `feature.status` 与 dict.get，R09 对普通 dict 运行发生 AttributeError；补齐其隐含 Record/directory_exists 辅助后，R12 对 `authorization=denied` 的合成任务仍返回 ready。后者说明算法未检查授权，不代表真实供应商命令已执行越权。
- **F14**：GUI Hook 先写 received ACK 再注入命令；R10/R11 证明相同 cmdId 再运行不注入，即使没有完成回执。它证明收到，不能证明执行成功，也没有自动接管语义。
- **F15**：当前官方 Claude Skills 采用目录中的 SKILL.md，Subagents 用 `.claude/agents/`；旧平铺 `.claude/skills/*.md`、`.claude/subagents/` 不应宣称可按当前原生机制自动加载。属于文档格式核查；尚未进行真实会话发现测试。来源见 [架构 §9](V4_ARCHITECTURE.md#9-执行适配与官方机制核查)。
- **F16**：`gate_checker` 的 exec 成功返回只有 command/exit_code，而 test_check 随后从 evidence.stdout 取测试输出；因此示例内部也存在证据断链（gate_checker:348–354、460–464）。未将 Markdown 伪代码当作已安装 Python 执行器。
- **未证实**：计数 `((count++))` 配合 set -e 的提前退出，在本机 Bash 3.2 上未复现；不能列为“已实测失败”。较新 Bash 的可移植性保留为待验证。早期探索错误预期已纠正，最终报告记录实际环境。

## 5. 隔离实测基准

执行：`python3 tests/p0_audit.py --output <新的输出目录>`。脚本拒绝覆盖旧运行；从固定 Git 基线逐文件检查输入，临时目录内执行，结束自动清理临时 fixture。无模型调用、无网络、无依赖安装、无真实项目初始化或发布。临时路径规范化为 `<fixture>`，日志内容未伪造。

环境：macOS / Darwin 24.5.0 arm64；Python 3.9.6；Bash 3.2.57。完整记录：[results.json](evidence/p0/results.json)。每条有 argv、cwd、退出码、输出文件及 SHA256。12 条观察断言成立，**这不等于 12 个产品场景通过**。

| 记录 | 变体 | 观察 |
|---|---|---|
| R01 | 原版安装 | 退出 1，缺旧路径 |
| R02 | 原版 list | 退出 0，但报告源目录不存在 |
| R03 | 原版 dry-run | 退出 1，未知参数 |
| R04 | Bash 语法检查 | 退出 0；语法正确不能证明安装正确 |
| R05 | 仅在临时副本修正源路径 | 退出 0，37 个工具文件 |
| R06 | 同一临时副本重复安装 | 退出 0，仍为 37 个文件，无重复新增 |
| R07 | 临时副本再改前置自增 | 退出 0，37 个文件，settings 未安装；仅诊断变体，不是正式修复 |
| R08 | 已有文件写入合成自定义内容后重装 | 退出 0，自定义内容保留 |
| R09 | 原 Ready Set 文档函数 + 普通 dict | 退出 1，AttributeError；无实际派单 |
| R12 | 同函数 + 显式辅助环境 | 退出 0，授权被拒任务仍列入 Ready |
| R10 | 合成 GUI .cmd + 原 Hook | 退出 0，产生 received ACK 和命令文本；未执行文本 |
| R11 | 同 cmdId 再次调用 Hook | 退出 0，无再次注入 |

## 6. 没有完成的验证

- 本轮没有在 Claude/Codex 中运行旧 `/new-feature → /check-gate → /approve-gate` 整条链；原版安装失败已经得到确定结论，绕过后真实模型行为仍待测。
- 未运行 HA Loop Desk，未验证真实云供应商或启用付费 API。
- 未声称已击穿旧 Gate，也未声称已实现能拒绝伪造报告的 V4 Gate。
- 156 文件的全量字节核对/引用盘点不等于所有示例的运行证明；独立逐项复核仍待第一轮评审。
- 本轮脚本是作者自测，独立评审、Owner 架构批准和所有 V4 端到端验收均未完成。

优先修复链：工具 manifest 与无损安装 → 统一 WP/授权/认领 → 真实证据 Gate → 恢复/多供应商 → GitHub 自动协调。详细任务见 [工作包](V4_WORK_PACKAGES.md)。
