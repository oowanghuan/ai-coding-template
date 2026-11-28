# Owner 决策账本

版本：0.2，2026-11-27。Owner 明确授权与 Project Lead 推荐分开记录。Advisor 可以建议，不能替 Owner 批准范围、费用或阶段放行。

## 1. 已有明确授权（不重复请批）

| ID | 决定与来源 | 允许范围 | 不包含 |
|---|---|---|---|
| OD-00 | 项目启动指令 | 只读盘点、合法只读实践研究、隔离验证、V4 分支、七份设计和计划 | 大规模实现、破坏迁移、main 写入、发布、额外付费 |
| OD-03 | Owner 后续指定 `v4/design` 并要求 Draft PR | 保留本地成果；公开性检查文件和提交历史后推送原公开仓库、开指向 main 的 Draft PR | 合入 main、改变可见性、发布私有研究原件 |
| OD-04 | Owner 授权专用 Issue、Advisor 仅追加评论、V4 独立每小时云轮询 | [#3](https://github.com/oowanghuan/ai-coding-template/issues/3) 为当前协作台账；Advisor 写入仅限该 Issue 评论 | Advisor 派单/修改代码、额外费用；授权不代表云任务已建成 |
| OD-05 | Owner 指示 Project Lead 接入 #3 | 本机每 15 分钟实际处理轮询、单实例、重启后补读；以 Owner 账号请审/复核；原范围内核查修订或说明异议 | 自动扩大开发范围、冒充独立签认、绕过沙盒或重新分配其他项目资源 |

本机 GitHub 身份已核实为 `oowanghuan`；不需要新增账号识别授权。Issue 已由 Owner 创建，直接接入 #3，不另建重复台账。

## 2. 重要裁定及未决选择

### OD-01：首个实现批次及最小产品范围

**推荐**：第一轮独立评审后，批准 WP-001（工具 manifest 与兼容修复）和 WP-101（核心协议），再按依赖逐批放行。以本地闭环 + 两个真实 CLI 为 Alpha，GitHub 自动协调为 Team Beta。详情见 [工作包](V4_WORK_PACKAGES.md)。

替代：一开始同步建设所有企业治理、云端调度与资产平台，会延迟核心验证。当前状态 **approved（仅 WP-001 / WP-101）**。Owner 原文及受托转记见 [7214229053](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7214229053)：仅放行 WP-001 和 WP-101。Project Lead 已核对来源和范围；后续包、合入、发布及新增费用不在此次授权内。

### OD-02：Team/Enterprise 的原子权威状态

**推荐**：GitHub 指定控制分支是唯一运行主状态，Issue 作为入口和可重建展示；以精确父提交和非强制 ref 更新实现可测的竞争事务，所有 Worker 通过统一写者请求变更。先在测试资源验证，不直接建立生产调度。

替代：以 Issue 为唯一人工状态，先不提供自动多机认领。优点是更简单；限制是 GitHub Issue 的普通字段更新不提供本方案需要的事务/资源锁，不能把“先查再写”宣传为排他。影响：推荐方案增加控制分支和投影维护，但避免本地 YAML/Issue 双主。细节与失效条件见 [架构 §3](V4_ARCHITECTURE.md#3-唯一权威状态源)。当前状态 **proposed**。

这属于重大架构取舍，需 Owner 明确决定。若未批准，后续只做本地协议或人工单写协调，不擅自部署控制分支。

### OD-06：第一轮独立评审与后续签认责任

**推荐**：在 #3 由独立 Advisor 上下文针对完整 SHA 审查七项交付，给出范围化 GO/REVISE/BLOCK；Owner 决定设计采纳和下一批放行。后续高风险实现包开工前落实独立技术评审、验收和合入身份。

Advisor 的账号若仍为 `oowanghuan`，记录独立执行上下文和只读证据，不能只凭账号或模型名声称独立；若使用其他账号，先向 Owner 报告身份并获得识别授权。影响：没有已绑定的独立评审主体时，作者检查仍然只能记为 self-test。

已有独立评审：[7210718044](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7210718044) 对 `17e65ec619b2e729cb81bd80f5d4f437099a27b6` 的 A01–A03 给出限定范围 GO；[7211690143](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7211690143) 对 `1fbe382a2ffce858f15ba1769e3068054e589f96` 的 A04 验收设计给出 GO，第一轮设计意见收口。随后 Owner 单独批准 OD-01 两个包。实现成果仍须按其新 SHA 独立评审，不把设计 GO 扩成产品验收或合入授权。Owner 已指示双方在既有范围自行核查/修订/复核，不逐条人工协调；重大取舍与阶段放行边界保持。

首批实现独立复核：[7217342565](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7217342565) 对 `673d6baa13283180b342f446bcadc17ad66efaf9` 给出 GO，关闭 WP-001/101 两项整改。Advisor 独立检查了代码、断言和作者的原始输出，本轮未执行候选代码。此结论是该版本、该范围的 review_passed，不是 main 合入、V4 Alpha 或后续阶段放行。

### OD-07：下一批本地执行与项目接入

当前状态 **approved，已授权开工**。Owner 经 Advisor 转记 [7218268841](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7218268841) 批准 PR #6 的范围；现有 Project Lead 会话由人工提醒接手，回执 [7219186379](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7219186379)。授权仅包含 WP-102（单机 Worker 登记、原子认领、受控本地 Runner）和 WP-103（项目 init/import/upgrade 预演、冲突保护和回退）。[工作包 §7](V4_WORK_PACKAGES.md#7-下一批开工方案od-07-已放行) 保留具体范围与验收边界。

已批准的范围：**按工作包 §7 实现 WP-102 和 WP-103，允许使用已独立复核、尚未合入 main 的 `673d6baa13283180b342f446bcadc17ad66efaf9` 作为精确依赖基线；独立分支和 Draft PR 交付。其他包、main 合入、发布、新增费用及无人值守模型执行不在本次放行内。**

原因：首批已提供声明校验，但仍没有真正的排他认领与可用项目接入闭环。WP-102/103 是下一段可实测的最短依赖链；GitHub 控制分支、完整供应商适配和云调度尚无必要提前展开。代价是必须补单机竞争、失效租约与中断写入证据，不能把这批通过称为双模型 Alpha。

建议继续由 Project Lead 实现、现有独立 Advisor 上下文技术复核。WP-102 属高风险，工程验收另由独立 Reviewer 在无发布凭证的隔离环境复跑关键争抢、旧租约拒绝与恢复用例；如只能做静态复核，须保留工程验收 pending，不能由实现者代签。具体独立执行能力在开工登记时落实，不假定模型不同就是独立。

实施分支 `v4/local-execution` 从计划提交 `228e9d6e4ca326b3f73c31686e4312a842d00c52` 建立；保留 PR #5/#6 的受审版本。普通修订沿既有授权推进，不重复请批。初次接手由人工触发；后来一次 active 自动接单已获限定 GO，不把初始人工接手改称自动执行。

2026-11-27 收口：[Advisor 7224552711](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7224552711) 对 `9d7f844ca7cf7784cff82cc725519216fb3202a5` 给出限定 GO：本机显式 external 固定合成任务，以及 WP-103 已实测的两条指南升级/回退路径。Advisor 确认该有限 external 实现属于 OD-07，未提出新的重大取舍。默认 direct 三项、真实供应商、完整恢复/Alpha 仍未验收。此 GO 不授权下一批、合入或发布；PR #8 的已审 SHA 冻结，收口和下一批方案另列分支。

### OD-08：本地证据门禁与签认治理批次

当前公开记录状态：**Project Lead 的会话内执行解释；Owner 直接阶段裁定尚无可供公开核对的记录**。此前使用 `approved` 未区分这两种证据强度，现按 [Advisor 7226757604](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7226757604) 更正。可核对的公开事实是 PR #9 提出 WP-201/203；本机会话确有 Owner 的“继续？”消息，Project Lead 将其解释为继续该具体方案并实施。该短句本身没有列出工作包，不应改写成 Owner 逐项批准的原话，也不能把 Project Lead 的公开转述视为独立确认。

已交付的实际范围是 WP-201（受控取证和确定性 Gate）与 WP-203（本地签认/契约变更治理）；本轮只修订已有交付的正确性与能力声明，不据此扩展工作包或启动新阶段。产品依赖基线为 `9d7f844ca7cf7784cff82cc725519216fb3202a5`，计划基线为 `711ba906b5ffbc1f86fba149c83a87404429dfd3`，均未合入；限用已验证的本机 external 边界，不把 direct 或全部 WP-102 自动视为通过。具体范围见 [工作包 §11](V4_WORK_PACKAGES.md#11-下一批具体方案od-08-proposed)。需要可公开确认的阶段放行时，以 Owner 对这两个工作包的直接裁定或其认可的可核对记录为准；本记录不伪造该裁定，也不导出原始会话或私有研究。

预期结果：一份自写的“测试通过”文件无法通过 Gate；真实受控运行可核对 SHA、命令、测试清单、日志和结果；独立签认绑定对象，关键契约变化和已失效签认阻止验收。仍不构成双模型 Alpha。

允许的最小执行扩展是为预审、固定哈希的测试入口增加有界取证路径，继续隔离候选代码且不给发布凭证。只记录/核验本地候选树，不进行实际合入；不增加通用 shell、常驻服务、供应商调用、联网/付费执行或 GitHub 权威状态服务。可信取证器与测试入口的具体固定版本须在执行前独立复核，路径名称和自报 actor 不构成信任依据。

两线可同时设计实现：201 取证/Gate 与 203 的记录模型/影响计算；203 的签认生效与联合 Gate 必须等待 201 已核验的证据接口和对应工程条件。共享协议由 Project Lead 单一集成。选择此批次可先补真实证据和验收能力，避免让后续模型输出提前变成“通过”；代价是双 CLI 的可见产品演示仍需下一批 301/302/303。

替代是本轮同时放行 WP-301 适配器；它会增加供应商运行环境与恢复分类的验证面，当前不推荐。OD-02、WP-202、301/302/303、main 合入和发布均不在推荐批准句内。

原拟请批事项为按 §11 实现 WP-201/203，并使用上述未合入基线作限定依赖；Project Lead 已按上述会话解释实施于独立 `v4/quality-governance` 分支，保留 PR #9 的计划 SHA。这是执行历史与来源说明，不新增公开授权证据。Advisor 的质量限定 GO 与当时的治理 REVISE 均不替代 Owner 阶段裁定。后续 [7227662743](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7227662743) 对 `534c1196738a5ec00d98587c0c77754605e27282` 给出治理锁定快照限定 GO，关闭两项修订；独立预审、A01、阶段验收以及禁止 main 合入/发布的边界均未变化。

### OD-09：本地 Lite Alpha 实现与限定依赖采纳

状态：**approved，Owner 已在本工作会话明确逐项批准**。Owner 最新指令明确
“同意 OD-09 的推荐方向”，列出限定依赖完整 SHA、WP-301/302/303 和隔离/费用限制。
随后补充 N 供应商边界；[Project Lead 开工转记](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7234932005)
标明会话指令来源，不冒充 Owner 账号下的一条独立裁定评论，不追认 OD-08。
此前 PR #11 的 proposed 状态是批准前历史。获批计划见
[工作包 §15](V4_WORK_PACKAGES.md#15-当前进度与下一批本地-lite-alphaod-09-proposed)。

**此次明确批准范围**：采纳 PR #10 的
`534c1196738a5ec00d98587c0c77754605e27282` 为限定依赖，批准 WP-301/302/303 的
本地 Lite Alpha 实现和隔离验收，按文件/接口并行推进。允许沿用合法现有 CLI 账号，
在独立审核的最小权限启动边界建立实际任务执行上下文，以验证 Claude Code/Codex
加载规则、真实任务和中断接管；无新增付费 API/服务、不共享凭证、不关闭或放宽 A01
候选执行隔离。具体启动器在执行前须独立复核；边界无法落实时保留成果并报告阻塞。
该确认只决定下一批使用既有成果，不把 OD-08 的历史解释追认为已发生的直接裁定。

纳入本批的集成补口包括初始化后的有效任务/Worker/授权入口、真实成果到现有固定
Python 取证及签认的连接、持续检查点和接管。真实额度恢复不可得时单列未测，不购买
额度、不绕限制；未满足原验收要求不得宣布完整 Alpha。可控故障注入和真实供应商证据分开。

不包含 Team/GitHub 权威状态服务、第二台机器/云端部署、实时目标引用观察服务、
main 合入、发布及新增费用。当前 Project Lead 轮询的权限边界保持；真实供应商任务
只在独立预审的启动边界完成后执行，不因本次批准关闭保护。

补充裁定：正式定位为 **Multi-provider, Model-agnostic Engineering Resource Pool**。
首批真实 Claude Code/Codex 验证不形成二元核心；Agent Tool、Model Provider、Model、
Credential Reference、Quota Group、Host、Worker、Session、Role、Assignment 分开表达。
共享额度按组处理，凭证仅引用，不保存明文。新增第三个合成 Adapter 的注册/匹配/认领/
暂停恢复/检查点/交付验收，不改核心调度、任务状态机与恢复协议。该扩展测试不增加订阅。

本批首要验收改为确定性调度不依赖 PMO 模型在线；八种 Worker 状态独立于任务；
有界退避、停止确认、保全与安全接管、恢复后回池和一次逻辑交付。先用故障注入完成
状态链，真实 CLI 及自然额度恢复单列证据；不得故意耗尽额度。新增机器、Dedicated/
Elastic/Restricted Worker 的接口当前明确，第二台机器和跨机部署另列具体方案与授权。

取舍：优先将已验证组件变成一条可用产品路径，延后 Team/Enterprise 平台建设；
成本集中在真实供应商执行边界与恢复一致性。替代是仅交付离线模拟器，风险更低，
但无法满足双供应商 Alpha。建议采用推荐范围，真实条件不足时精确降级声明而不伪造通过。

## 3. 环境待落实，非新增审批门

初次交付时，本机没有创建/核验云端每小时 Advisor 的调度接口。此后 [Advisor 评论 7203311332](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7203311332) 报告其侧已核实云端配置启用，但检查时尚无可见定时运行记录，本条为主动评审。因此分别记录“Advisor 侧报告配置已启用”和“本机尚无云端定时运行实证”，不再笼统说所有环境未启用。不能用本机任务代替云端验收。

沿用 Owner/Advisor 现有的独立云调度器，拿到实际运行记录后进行只读核验。若需新付费服务、扩大凭证权限或默认分支部署，才提交相应裁定。本机轮询恢复为只读核查/已核查文字回执；候选执行路径按 A01 禁用，普通意见由 Project Lead 在已授权范围处理，无需 Owner 逐条审批。

V3 资产保留、Lite 默认轻量、CLI 优先、现有项目 dry-run/保全、普通意见原范围修订均已有方向与授权，不额外制造逐项审批。旧资产实际删除、公开正式发布及破坏迁移仍需另行批准。
