# 01_COMMIT_RULES.md
# Git Commit 规范

> 版本：v1.0
> 最后更新：2024-12-09
> 适用范围：所有 Git 提交

---

## 1. 概述

本文档定义项目的 Git Commit 规范，遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准，确保：
- 提交历史清晰可读
- 支持自动化 CHANGELOG 生成
- 便于代码审查
- Claude Code 能生成规范的提交信息

---

## 2. Commit 消息格式

### 2.1 基本格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 2.2 格式说明

| 部分 | 必填 | 说明 |
|------|------|------|
| type | 是 | 提交类型 |
| scope | 否 | 影响范围 |
| subject | 是 | 简短描述（50 字符以内） |
| body | 否 | 详细描述（每行 72 字符以内） |
| footer | 否 | 关联 Issue 或 Breaking Change |

---

## 3. Type 类型

### 3.1 主要类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat: 添加用户登录功能 |
| `fix` | 修复 Bug | fix: 修复登录验证失败问题 |
| `docs` | 文档更新 | docs: 更新 API 文档 |
| `style` | 代码格式（不影响逻辑） | style: 格式化代码 |
| `refactor` | 重构（不添加功能或修复） | refactor: 重构用户模块 |
| `test` | 测试相关 | test: 添加登录单元测试 |
| `chore` | 构建/工具/依赖 | chore: 升级依赖版本 |

### 3.2 其他类型

| Type | 说明 | 示例 |
|------|------|------|
| `perf` | 性能优化 | perf: 优化列表渲染性能 |
| `build` | 构建系统 | build: 配置生产环境打包 |
| `ci` | CI 配置 | ci: 添加 GitHub Actions |
| `revert` | 回滚 | revert: 回滚 feat: 添加登录 |

---

## 4. Scope 范围

### 4.1 常用 Scope

```
# 功能模块
auth          # 认证相关
user          # 用户模块
project       # 项目模块
dashboard     # 看板模块

# 技术层面
api           # API 相关
ui            # UI 相关
db            # 数据库相关
config        # 配置相关

# 文档
docs          # 文档相关
readme        # README
changelog     # CHANGELOG
```

### 4.2 Scope 示例

```bash
feat(auth): 添加 JWT 认证
fix(user): 修复用户头像上传失败
docs(api): 更新用户接口文档
style(ui): 统一按钮样式
refactor(dashboard): 重构看板数据加载
test(auth): 添加登录功能测试
chore(deps): 升级 Vue 到 3.4
```

---

## 5. Subject 主题

### 5.1 书写规则

1. **使用祈使句**：描述做了什么，不是描述状态
2. **首字母不大写**（英文时）
3. **不使用句号结尾**
4. **控制在 50 字符以内**

### 5.2 正确示例

```bash
# 正确
feat: 添加用户登录功能
fix: 修复密码验证逻辑
docs: 更新部署文档

# 错误
feat: 添加了用户登录功能。   # 不用"了"，不用句号
fix: Fixed password bug.      # 首字母不大写，不用过去式
docs: 更新                     # 太简略
```

### 5.3 中文 vs 英文

```bash
# 中文（推荐用于内部项目）
feat: 添加用户登录功能
fix: 修复订单支付失败问题

# 英文（开源项目或国际团队）
feat: add user login feature
fix: fix order payment failure
```

---

## 6. Body 详情

### 6.1 何时需要 Body

- 需要解释「为什么」做这个改动
- 改动复杂，需要更多说明
- 有特殊的实现考虑

### 6.2 Body 格式

```bash
feat(auth): 添加 OAuth2.0 登录

支持通过 GitHub 和 Google 账号登录。

实现细节：
- 使用 passport.js 处理 OAuth 流程
- 添加 /auth/github 和 /auth/google 路由
- 用户首次登录时自动创建账号

相关文档：docs/auth/oauth.md
```

### 6.3 Body 规则

- 空一行后开始写 Body
- 每行控制在 72 字符以内
- 解释「什么」和「为什么」，而非「如何」

---

## 7. Footer 页脚

### 7.1 关联 Issue

```bash
feat(user): 添加用户头像功能

Closes #123
Fixes #456
Refs #789
```

### 7.2 Breaking Change

```bash
feat(api)!: 重构用户 API 响应格式

BREAKING CHANGE: 用户 API 响应格式变更

Before:
{
  "user": { "id": 1, "name": "张三" }
}

After:
{
  "data": { "id": 1, "name": "张三" }
}

迁移指南：
1. 更新所有调用 /api/users 的代码
2. 将 response.user 改为 response.data
```

---

## 8. 特殊情况

### 8.1 多人协作

```bash
feat(dashboard): 添加项目进度图表

Co-authored-by: 张三 <zhangsan@example.com>
Co-authored-by: Claude Code <noreply@anthropic.com>
```

### 8.2 Claude Code 提交

```bash
feat(user): 添加用户列表分页功能

实现用户列表的服务端分页，支持：
- 每页 10/20/50 条记录
- 页码跳转
- 总数显示

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 8.3 回滚提交

```bash
revert: feat(user): 添加用户头像功能

This reverts commit abc1234.

原因：头像上传功能存在安全漏洞，暂时回滚。
```

### 8.4 合并提交

```bash
merge: 合并 feature/user-auth 到 main

包含以下功能：
- 用户登录
- 用户注册
- 密码重置
```

---

## 9. 完整示例

### 9.1 简单提交

```bash
feat: 添加登录页面
fix: 修复表单验证错误
docs: 更新 README
style: 格式化代码
chore: 更新依赖
```

### 9.2 带 Scope 的提交

```bash
feat(auth): 添加 JWT 认证中间件
fix(user): 修复用户头像上传失败
docs(api): 完善用户接口文档
refactor(dashboard): 优化数据加载逻辑
test(auth): 添加登录功能单元测试
```

### 9.3 完整格式提交

```bash
feat(dashboard): 添加项目进度追踪功能

实现项目进度的可视化追踪，包括：
- 按阶段显示进度条
- 任务完成率统计
- 阻塞项高亮显示

技术实现：
- 使用 ECharts 绘制进度图
- 数据从 PROGRESS_LOG.yaml 解析

Closes #45
Refs #32

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 10. Claude Code 使用指南

### 10.1 提交检查清单

- [ ] Type 是否正确
- [ ] Subject 是否清晰
- [ ] 是否在 50 字符以内
- [ ] 是否需要 Body 解释
- [ ] 是否有关联 Issue
- [ ] 是否有 Breaking Change

### 10.2 提交命令

```bash
# 简单提交
git commit -m "feat: 添加用户登录功能"

# 带 Scope
git commit -m "feat(auth): 添加 JWT 认证"

# 完整格式（使用 HEREDOC）
git commit -m "$(cat <<'EOF'
feat(dashboard): 添加项目进度追踪

实现项目进度的可视化追踪功能。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 10.3 常见错误

```bash
# 错误：类型不对
update: 更新登录页面      # 没有 update 类型，应该用 feat 或 fix

# 错误：太笼统
fix: 修复 bug            # 太笼统，应说明修复什么

# 错误：混合多个改动
feat: 添加登录和修复表单   # 应该拆分为多个提交

# 错误：没有意义
chore: update            # 没有说明更新什么
```

---

## 附录

### A. Type 速查表

| Type | 含义 | 会出现在 CHANGELOG |
|------|------|-------------------|
| feat | 新功能 | ✅ Features |
| fix | 修复 | ✅ Bug Fixes |
| docs | 文档 | ❌ |
| style | 格式 | ❌ |
| refactor | 重构 | ❌ |
| perf | 性能 | ✅ Performance |
| test | 测试 | ❌ |
| build | 构建 | ❌ |
| ci | CI | ❌ |
| chore | 杂项 | ❌ |
| revert | 回滚 | ✅ Reverts |

### B. 常用动词

| 中文 | 英文 | 使用场景 |
|------|------|----------|
| 添加 | add | 新增功能/文件 |
| 修复 | fix | 修复问题 |
| 更新 | update | 更新已有内容 |
| 删除 | remove | 删除功能/文件 |
| 重构 | refactor | 重构代码 |
| 优化 | optimize | 优化性能 |
| 移动 | move | 移动文件 |
| 重命名 | rename | 重命名 |
