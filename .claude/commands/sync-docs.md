# /sync-docs - 检查文档与代码一致性

你是一个 AI 协作开发助手。用户请求检查文档与代码的一致性，发现文档过时或不匹配的问题。

## 参数

- `$ARGUMENTS`：功能模块路径或项目路径
  - `--fix`：自动修复可修复的问题
  - `--type=TYPE`：检查类型（all | api | schema | modules）
  - `--strict`：严格模式，警告也视为错误

## 用法

```
/sync-docs docs/my-feature
/sync-docs docs/my-feature --type=api
/sync-docs ./my-project --fix
/sync-docs docs/legacy-app --strict
```

## 执行步骤

### 1. 定位文档和代码

```
解析参数确定：
  - 功能目录：docs/{feature}/
  - 项目代码：从 10_CONTEXT.md 或 90_PROGRESS_LOG.yaml 获取原始项目路径

检查必需文件：
  - docs/{feature}/10_CONTEXT.md
  - docs/{feature}/20_API_SPEC.md（如果存在）
  - docs/{feature}/_foundation/03_DATA_MODEL.md（如果存在）
```

### 2. 检查 API 文档一致性

```
如果存在 20_API_SPEC.md：

对每个文档中的端点：
  1. 在代码中查找对应路由定义
  2. 比较 method、path
  3. 比较请求参数
  4. 比较响应类型

对每个代码中的端点：
  1. 在文档中查找对应定义
  2. 标记未文档化的端点

生成差异报告：
  - added: 代码有，文档没有
  - removed: 文档有，代码没有
  - modified: 存在但不一致
  - matched: 一致
```

### 3. 检查数据模型一致性

```
如果存在 03_DATA_MODEL.md：

对每个文档中的模型：
  1. 在 ORM Schema 中查找对应定义
  2. 比较字段名、类型
  3. 比较关系定义

对每个 Schema 中的模型：
  1. 在文档中查找对应定义
  2. 标记未文档化的模型

生成差异报告：
  - 新增字段
  - 删除字段
  - 类型变更
  - 关系变更
```

### 4. 检查模块划分一致性

```
如果存在模块划分文档：

对比文档中的模块列表与实际目录结构：
  - 新增目录（未文档化）
  - 删除目录（文档过时）
  - 模块描述是否准确
```

### 5. 生成同步报告

```
📊 文档同步检查报告

功能：{feature_name}
检查时间：{datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 总体状态：{✅ 同步 | ⚠️ 有差异 | ❌ 严重不一致}

| 类型 | 文档项 | 代码项 | 匹配 | 差异 |
|------|--------|--------|------|------|
| API 端点 | 15 | 18 | 12 | 6 |
| 数据模型 | 8 | 8 | 7 | 1 |
| 模块 | 5 | 6 | 4 | 2 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## API 差异详情

### 🆕 新增端点（代码有，文档没有）

| 方法 | 路径 | 来源 |
|------|------|------|
| POST | /api/users/batch | src/routes/user.ts:45 |
| DELETE | /api/users/:id | src/routes/user.ts:62 |

### 🗑️ 移除端点（文档有，代码没有）

| 方法 | 路径 | 文档位置 |
|------|------|----------|
| GET | /api/deprecated | 20_API_SPEC.md:120 |

### ⚠️ 变更端点

| 端点 | 差异类型 | 详情 |
|------|----------|------|
| GET /api/users | 参数变更 | 新增 `status` 参数 |
| POST /api/orders | 响应变更 | 返回结构变化 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 数据模型差异详情

### User 模型

| 字段 | 文档 | 代码 | 状态 |
|------|------|------|------|
| id | String | String | ✅ |
| email | String | String | ✅ |
| avatar | - | String | 🆕 新增 |
| phone | String | - | 🗑️ 移除 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 建议操作

{如果有差异}
1. **更新 API 文档**：
   - 添加 2 个新端点
   - 移除 1 个过时端点
   - 更新 2 个变更端点

2. **更新数据模型**：
   - User: 添加 avatar 字段，移除 phone 字段

3. **重新生成文档**（可选）：
   /reverse-api {project_path}
   /reverse-schema {project_path}

{如果使用 --fix}
📝 自动修复结果：
  ✅ 已添加 2 个新端点到文档
  ✅ 已标记 1 个端点为 [deprecated]
  ⚠️ 响应结构变更需手动确认

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6. 保存检查结果

```yaml
# docs/{feature}/SYNC_REPORT.yaml
meta:
  feature: "{feature}"
  checked_at: "{datetime}"
  status: "out_of_sync"  # in_sync | out_of_sync | error

summary:
  api:
    total_in_doc: 15
    total_in_code: 18
    matched: 12
    added: 3
    removed: 1
    modified: 2
  schema:
    total_in_doc: 8
    total_in_code: 8
    matched: 7
    modified: 1

differences:
  api:
    added:
      - method: POST
        path: /api/users/batch
        source: src/routes/user.ts:45
    removed:
      - method: GET
        path: /api/deprecated
        doc_location: 20_API_SPEC.md:120
    modified:
      - path: /api/users
        type: params_added
        details: "新增 status 参数"

  schema:
    modified:
      - model: User
        changes:
          - field: avatar
            type: added
          - field: phone
            type: removed

recommendations:
  - action: "update_api_doc"
    priority: high
    details: "添加 2 个新端点"
  - action: "update_schema_doc"
    priority: medium
    details: "更新 User 模型字段"
```

## --fix 模式说明

```
可自动修复的项目：
  ✅ 添加新端点/模型到文档
  ✅ 标记移除的端点为 [deprecated]
  ✅ 更新简单的类型变更

需手动修复的项目：
  ❌ 响应结构复杂变更
  ❌ 业务语义变更
  ❌ 关系类型变更

自动修复会：
  1. 备份原文档到 .backup/
  2. 在变更处添加 [auto-fixed] 标记
  3. 生成修复日志
```

## 输出格式选项

```
默认：终端输出 + SYNC_REPORT.yaml

--format=json：输出 JSON 格式报告
--format=md：输出 Markdown 格式报告
--quiet：只输出统计摘要
```

## 错误处理

```
如果找不到文档：
  ❌ 未找到功能文档

  缺失文件：
  - docs/{feature}/10_CONTEXT.md

  建议：
  先执行 /integrate-project 创建文档

如果找不到代码：
  ⚠️ 无法定位原始项目代码

  请确认 10_CONTEXT.md 或 90_PROGRESS_LOG.yaml 中包含项目路径
  或使用：/sync-docs {feature} --code-path={path}
```

## 注意事项

1. **只读操作**：除非使用 --fix，否则不修改任何文件
2. **备份**：--fix 会自动备份原文件
3. **定期检查**：建议在每次代码变更后运行
4. **CI 集成**：可在 CI 中使用 --strict 确保文档同步

## 关联命令

- `/scan-project` - 项目扫描
- `/integrate-project` - 项目整合
- `/reverse-api` - 重新生成 API 文档
- `/reverse-schema` - 重新生成数据模型文档
