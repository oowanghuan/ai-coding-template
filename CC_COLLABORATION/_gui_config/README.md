# _gui_config - GUI 依赖配置

> **重要提示**：此目录的文件被 ha-loop-desk GUI 项目直接引用，修改路径需同步更新 ha-loop-desk。

---

## 文件说明

| 文件 | 用途 | ha-loop-desk 引用位置 |
|------|------|---------------------|
| `WORKFLOW_TEMPLATE.yaml` | 全局工作流框架配置 | `configLoader.ts` |
| `PHASE_GATE.yaml` | Phase Gate UI 配置 | `configLoader.ts` |

---

## 修改注意事项

1. **路径变更**：如需修改文件路径，必须同步更新：
   - `ha-loop-desk/src/renderer/services/configLoader.ts`

2. **字段变更**：如需修改 YAML 字段结构，必须同步更新：
   - `ha-loop-desk/src/shared/schema-discovery/template-scanner.ts`

3. **版本兼容**：修改前请确认 ha-loop-desk 版本兼容性

---

## 相关项目

- **ha-loop-desk**: GUI 控制台项目
- **ai-coding-template**: 模板源项目

---

_最后更新：2026-01-09_
