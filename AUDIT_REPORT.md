# AI Coding Template - 深度审计报告（仅本仓库）

> 范围：ai-coding-template 仓库（不含 _backup、不含已安装命令目录）
> 目的：流程合理性 + 工具/模板/规则一致性深度评审
> 结论：流程设计优秀，但存在多处“规范-模板-命令”断链，需优先修复一致性

---

## 1. 发现项（按严重度排序）

### HIGH

1) `/new-feature` 不生成 `PHASE_GATE.yaml`/`PHASE_GATE_STATUS.yaml`，但 `/check-gate` 要求其存在，导致 Gate 流程直接失败。
- `CC_COLLABORATION/05_tools/slash-commands/new-feature.md:20-28`
- `CC_COLLABORATION/05_tools/slash-commands/check-gate.md:91-105`

2) `/check-gate` 仍依赖 `gate_checker` skill，但 skills 体系已宣告合并且不存在该 skill，命令规范与技能体系断链。
- `CC_COLLABORATION/05_tools/slash-commands/check-gate.md:129-137`
- `CC_COLLABORATION/05_tools/skills/README.md:111-124`

3) Phase 2 Gate 规则检查目标写成 `11_*.md`，而实际模板为 `20_API_SPEC.md` / `21_UI_FLOW_SPEC.md`，Spec Gate 质量校验失效。
- `CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml:63-96`

4) Subagents 声明依赖 `spec_validator` / `progress_updater` / `changelog_updater` / `openai_expert_review` 等 Skills，但 Skills 目录只定义 5 个且不包含这些，工具链定义失配。
- `CC_COLLABORATION/05_tools/subagents/README.md:37-59,90-118`
- `CC_COLLABORATION/05_tools/skills/README.md:30-42`

5) Demo 产物格式与路径不一致：
- `/gen-demo` 生成 HTML
- Gate 规则要求 `_demos/*.vue`
- 进度日志模板指向 `playgrounds/{feature}/Demo.vue`
- `CC_COLLABORATION/05_tools/slash-commands/gen-demo.md:56-64`
- `CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml:109-115`
- `CC_COLLABORATION/03_templates/_shared/90_PROGRESS_LOG_TEMPLATE.yaml:75-85`

### MED

6) 工具安装脚本的“数量/类型”与工具文档不一致（脚本写 10 commands/13 skills/4 subagents；工具 README 写 25/6/5；skills README 写 5），造成可执行范围误判。
- `scripts/init-claude-tools.sh:94-102`
- `CC_COLLABORATION/05_tools/README.md:70-151`
- `CC_COLLABORATION/05_tools/skills/README.md:26-42`

7) `/daily-summary` 输出路径仍指向 `docs/_system/...`，与当前 `docs/_foundation` 体系冲突。
- `CC_COLLABORATION/05_tools/slash-commands/daily-summary.md:30-32,173`

8) `/new-feature` 模板示例引用 `docs/_system/CC_COLLABORATION/04_AI_WORKFLOW.md`（已移除）。
- `CC_COLLABORATION/05_tools/slash-commands/new-feature.md:198-201`

9) `START_NEW_FEATURE` Recipe 与 `/new-feature` 规范对目录结构描述不一致（是否创建 `91_DAILY_SUMMARY/`、是否创建 `_demos/`）。
- `CC_COLLABORATION/01_workflow/recipes/START_NEW_FEATURE.md:44-49`
- `CC_COLLABORATION/05_tools/slash-commands/new-feature.md:20-28`

10) `/new-feature` 中的 `90_PROGRESS_LOG.yaml` 示例结构与模板结构字段不一致（如 `meta.feature` vs `meta.feature_id`、缺失 `stats` 等）。
- `CC_COLLABORATION/05_tools/slash-commands/new-feature.md:212-259`
- `CC_COLLABORATION/03_templates/_shared/90_PROGRESS_LOG_TEMPLATE.yaml:8-200`

11) 项目级文档结构描述仍包含 `docs/_foundation/00_PROJECT_CONTEXT.md`，但模板体系未提供该文件，存在“死引用”。
- `CC_COLLABORATION/01_workflow/04_REFERENCE.md:60-69`
- `CC_COLLABORATION/_project_context/COLLABORATION_GUIDE.md:187`

12) `/check-progress` 阶段命名与主流程不一致（Phase 3 UI Flow / Phase 4 Review vs Demo/Design）。
- `CC_COLLABORATION/05_tools/slash-commands/check-progress.md:54-59`

### LOW

13) `docs/README.md` 的文档编号规则与当前模板/阶段命名不一致，易误导新人。
- `docs/README.md:30-39`

14) Foundation Gate 文档仍提 `/check-foundation-gate`，主流程已迁移到 `/check-gate --phase=0`。
- `CC_COLLABORATION/03_templates/00_foundation/00_FOUNDATION_GATE.md:66-84`

---

## 2. 审计结论（整体评价）

- **流程合理性**：8+1 阶段结构完整，Phase 0.5 的“需求起源层”能显著降低需求漂移风险，整体设计优秀。
- **可执行性风险**：多处文档/模板/命令的路径和命名不一致，导致实际执行时“流程中断”概率高。
- **模板质量**：覆盖全面、结构细致，但模板命名/编号规则缺少统一落地，会削弱稳定性。
- **维护性**：版本漂移已显现（命令数量、技能列表、目录结构、旧路径引用），缺乏单一事实源（SSOT）。

---

## 3. SSOT 对照表（建议的单一事实源与派生项）

- **命令与工具清单**
  - SSOT：`CC_COLLABORATION/05_tools/README.md`
  - 派生：`scripts/init-claude-tools.sh` 的工具数量/列表说明；`CC_COLLABORATION/01_workflow/04_REFERENCE.md` 的命令速查表；`README.md` 的工具列表

- **工具执行规范**
  - SSOT：`CC_COLLABORATION/05_tools/slash-commands/*.md`
  - 派生：`CC_COLLABORATION/01_workflow/recipes/*` 对应步骤、`CLAUDE_INIT.md` 初始化步骤

- **模板规范**
  - SSOT：`CC_COLLABORATION/03_templates/README.md` + 实际模板文件
  - 派生：`docs/README.md` 的结构与编号规则；`CC_COLLABORATION/01_workflow/04_REFERENCE.md` 的模板清单

- **Phase Gate 规则**
  - SSOT：`CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml`
  - 派生：`CC_COLLABORATION/07_phase_gate/README.md` 的解释与示例

- **Feature 目录结构**
  - SSOT：`CC_COLLABORATION/03_templates/README.md`
  - 派生：`/new-feature` 规范、`START_NEW_FEATURE` recipe、`docs/README.md`

- **进度日志结构**
  - SSOT：`CC_COLLABORATION/03_templates/_shared/90_PROGRESS_LOG_TEMPLATE.yaml`
  - 派生：`/new-feature` 的示例 YAML、`/check-progress` 与 `/start-day` 的解析逻辑

---

## 4. 逐条修复指引（不修改文件，仅建议）

1) **修复 `/new-feature` 与 Gate 机制断链**
- 目标：`/new-feature` 输出必须包含 `PHASE_GATE.yaml` 与 `PHASE_GATE_STATUS.yaml`
- 受影响：`CC_COLLABORATION/05_tools/slash-commands/new-feature.md`
- 依赖模板：`CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml`、`PHASE_GATE_STATUS_TEMPLATE.yaml`

2) **修复 Phase 2 Gate 规则目标文件**
- 目标：`phase_2_spec.quality_checks.target` 从 `11_*.md` 改为 `20_API_SPEC.md`/`21_UI_FLOW_SPEC.md`
- 受影响：`CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml`

3) **统一 Demo 产物与路径**
- 目标：三方一致：`/gen-demo` 产物、Gate 规则、进度日志模板
- 受影响：
  - `CC_COLLABORATION/05_tools/slash-commands/gen-demo.md`
  - `CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml`
  - `CC_COLLABORATION/03_templates/_shared/90_PROGRESS_LOG_TEMPLATE.yaml`
- 说明：确定最终产物是 HTML 还是 Vue，并统一目录（`_demos/` 或 `playgrounds/`）

4) **清理旧路径引用（docs/_system、04_AI_WORKFLOW）**
- 目标：统一到 `docs/_foundation` + 现行 workflow 文件
- 受影响：
  - `CC_COLLABORATION/05_tools/slash-commands/daily-summary.md`
  - `CC_COLLABORATION/05_tools/slash-commands/new-feature.md`

5) **修复 Skills/Subagents 声明与实际列表的断链**
- 目标：Subagent 调用的 Skills 必须存在或改为“内置逻辑”
- 受影响：`CC_COLLABORATION/05_tools/subagents/README.md`、`CC_COLLABORATION/05_tools/skills/README.md`

6) **统一工具数量与说明**
- 目标：脚本文案与工具 README 保持一致
- 受影响：`scripts/init-claude-tools.sh`、`CC_COLLABORATION/05_tools/README.md`

7) **修正文档结构描述与模板一致性**
- 目标：`docs/README.md` 与 `04_REFERENCE.md` 的目录结构与模板一致
- 受影响：`docs/README.md`、`CC_COLLABORATION/01_workflow/04_REFERENCE.md`

8) **统一阶段命名（Demo/Design/Review/UI Flow）**
- 目标：所有命令输出与参考文档使用同一阶段名称
- 受影响：`/check-progress`、`01_workflow` 文档与模板

---

## 5. 结语

本框架的核心设计（Phase Gate + 文档驱动 + PM Driver）非常完整，是高质量协作框架的基础形态。当前主要问题集中在“规范层的一致性”，一旦修复上述断链点，框架整体可执行性会显著提升。

