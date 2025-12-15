# CHANGELOG_TEMPLATE.md
# 文档变更日志模板

---

> **使用说明**
> 1. 复制此模板到对应目录，重命名为 `{文档名}_CHANGELOG.md`
> 2. 每次文档变更时添加新条目
> 3. 最新版本放在最上面
> 4. 删除本使用说明块

---

# {文档名称} CHANGELOG

> 关联文档：`{文档路径}`
> 最后更新：{YYYY-MM-DD}

---

## 版本记录

### [v1.2.0] - {YYYY-MM-DD}

**变更类型**：{Major | Minor | Patch}
**审批人**：{@username}

#### Added（新增）
- {新增内容描述}

#### Changed（变更）
- {变更内容描述}

#### Deprecated（废弃）
- {废弃内容描述}

#### Removed（移除）
- {移除内容描述}

#### Fixed（修复）
- {修复内容描述}

#### Security（安全）
- {安全相关变更}

---

### [v1.1.0] - {YYYY-MM-DD}

**变更类型**：Minor
**审批人**：{@username}

#### Changed
- {变更内容描述}

#### Fixed
- {修复内容描述}

---

### [v1.0.0] - {YYYY-MM-DD}

**变更类型**：Major（初始版本）
**审批人**：{@username}

#### Added
- 初始版本发布
- {功能点 1}
- {功能点 2}
- {功能点 3}

---

## 版本号说明

遵循 [Semantic Versioning](https://semver.org/) 规范：

| 版本类型 | 格式 | 触发条件 |
|----------|------|----------|
| Major | X.0.0 | 不兼容的变更，Breaking Change |
| Minor | 0.X.0 | 向后兼容的新功能 |
| Patch | 0.0.X | 向后兼容的 Bug 修复 |

---

## 变更类型说明

| 类型 | 说明 |
|------|------|
| Added | 新增的功能或内容 |
| Changed | 已有功能的变更 |
| Deprecated | 即将废弃的功能 |
| Removed | 已移除的功能 |
| Fixed | 修复的问题 |
| Security | 安全相关的修复 |

---

## 模板使用示例

```markdown
### [v2.0.0] - 2024-12-15

**变更类型**：Major
**审批人**：@Huan

#### Added
- 添加用户权限管理章节
- 添加 API 错误码附录

#### Changed
- **Breaking**: 将 API 响应格式从 `{ user: {...} }` 改为 `{ data: {...} }`
- 更新技术架构图

#### Removed
- 移除已废弃的 v1 API 文档

#### Fixed
- 修正第 3.2 节的代码示例错误
```
