# changelog_updater - 更新 CHANGELOG

## 能力描述

自动更新文档的 CHANGELOG 文件，记录文档变更历史。支持所有带有对应 CHANGELOG 的文档类型。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| doc_type | string | 是 | 文档类型：`context`, `spec`, `design` |
| change_type | string | 是 | 变更类型：`added`, `changed`, `fixed`, `removed` |
| description | string | 是 | 变更描述 |
| version | string | 否 | 版本号，默认自动递增 |

## 输出

- 更新后的 CHANGELOG 文件

## CHANGELOG 文件对应关系

| 文档 | CHANGELOG |
|------|-----------|
| `10_CONTEXT.md` | `10_CONTEXT_CHANGELOG.md` |
| `21_UI_FLOW_SPEC.md` | `11_SPEC_CHANGELOG.md` |
| `20_API_SPEC.md` | `11_SPEC_CHANGELOG.md` |
| `40_DESIGN_FINAL.md` | `40_DESIGN_CHANGELOG.md` |

## 执行步骤

### 1. 确定 CHANGELOG 文件

```javascript
const changelogMap = {
  'context': '10_CONTEXT_CHANGELOG.md',
  'spec': '11_SPEC_CHANGELOG.md',
  'design': '40_DESIGN_CHANGELOG.md'
}

const changelogPath = `docs/${feature}/${changelogMap[doc_type]}`
```

### 2. 读取现有 CHANGELOG

如果文件不存在，从模板创建：

```markdown
# {Doc Type} 变更日志

> 功能模块：{feature}
> 主文档：{main_doc}

---

## 变更记录

<!-- 按时间倒序排列 -->
```

### 3. 生成变更条目

```markdown
### [{version}] - {date}

#### {change_type_label}
- {description}
```

变更类型标签：
- `added` → **新增**
- `changed` → **变更**
- `fixed` → **修复**
- `removed` → **移除**

### 4. 插入到文件

在 `## 变更记录` 下方插入新条目：

```markdown
## 变更记录

### [v1.2] - 2024-12-11

#### 新增
- 添加了"记住我"功能的 UI 规格

### [v1.1] - 2024-12-10

#### 变更
- 更新了登录表单字段定义

### [v1.0] - 2024-12-09

#### 新增
- 初始版本
```

### 5. 输出结果

```
✅ CHANGELOG 已更新

文件：docs/{feature}/{changelog_file}
版本：v1.2
类型：新增
描述：添加了"记住我"功能的 UI 规格

最近 3 条记录：
• [v1.2] 新增 - 添加了"记住我"功能的 UI 规格
• [v1.1] 变更 - 更新了登录表单字段定义
• [v1.0] 新增 - 初始版本
```

## 示例

### 示例 1：记录 SPEC 变更

```
请使用 changelog_updater skill：
- feature: user-auth
- doc_type: spec
- change_type: added
- description: 添加了邮箱验证流程的 UI 规格
```

**输出**：

```markdown
### [v1.3] - 2024-12-11

#### 新增
- 添加了邮箱验证流程的 UI 规格
```

### 示例 2：记录 DESIGN 修复

```
请使用 changelog_updater skill：
- feature: user-auth
- doc_type: design
- change_type: fixed
- description: 修正了 Token 刷新接口的响应格式
```

**输出**：

```markdown
### [v1.1] - 2024-12-11

#### 修复
- 修正了 Token 刷新接口的响应格式
```

### 示例 3：批量记录变更

```
请使用 changelog_updater skill 记录以下变更：
- feature: user-auth
- doc_type: context
- changes:
    - type: added
      description: 新增社交登录需求（Google、GitHub）
    - type: changed
      description: 将密码最小长度从 6 改为 8
    - type: removed
      description: 移除手机号登录需求
```

**输出**：

```markdown
### [v1.2] - 2024-12-11

#### 新增
- 新增社交登录需求（Google、GitHub）

#### 变更
- 将密码最小长度从 6 改为 8

#### 移除
- 移除手机号登录需求
```

## 版本号规则

### 自动递增规则

| 变更类型 | 版本变化 | 示例 |
|---------|---------|------|
| added（重大功能） | Minor +1 | v1.1 → v1.2 |
| changed | Minor +1 | v1.1 → v1.2 |
| fixed | Patch +1 | v1.1 → v1.1.1 |
| removed | Minor +1 | v1.1 → v1.2 |

### 手动指定版本

可以通过 `version` 参数手动指定版本号，跳过自动递增。

## 注意事项

1. **时间顺序**：新条目插入到顶部，保持倒序排列
2. **格式一致**：确保缩进和格式与现有内容一致
3. **关联主文档**：同时更新主文档的版本号（如果有）
4. **批量变更**：多个变更可以合并到同一个版本条目

## 关联工具

- `doc_generator` - 生成文档时创建对应的 CHANGELOG
- `spec_validator` - 验证变更后的 SPEC
- `release_summarizer` - 汇总所有 CHANGELOG 到发布说明
