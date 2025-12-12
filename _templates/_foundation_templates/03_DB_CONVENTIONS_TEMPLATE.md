# 03_DB_CONVENTIONS.md
# 数据库设计规范

> 版本：v1.0
> 最后更新：{date}
> 状态：Draft

---

## 1. 概述

本文档定义了 {project_name} 项目的数据库设计规范，所有数据表设计必须遵循本规范。

---

## 2. 命名规范

### 2.1 表名

- 使用小写字母和下划线
- 使用名词复数
- 前缀规则：`{prefix}_`（可选）

```
# 示例
users
user_profiles
order_items
```

### 2.2 字段名

- 使用小写字母和下划线（snake_case）
- 主键统一使用 `id`
- 外键格式：`{related_table}_id`
- 时间字段：`created_at`, `updated_at`, `deleted_at`

### 2.3 索引名

```
idx_{table}_{column}          # 普通索引
uk_{table}_{column}           # 唯一索引
pk_{table}                    # 主键索引
```

---

## 3. 通用字段

所有表必须包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | BIGINT / UUID | 主键 |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 更新时间 |
| `deleted_at` | TIMESTAMP | 软删除时间（可选） |

---

## 4. 数据类型规范

### 4.1 推荐类型

| 数据 | 推荐类型 | 说明 |
|------|----------|------|
| 主键 | BIGINT / UUID | - |
| 字符串 | VARCHAR(n) | 指定最大长度 |
| 长文本 | TEXT | - |
| 整数 | INT / BIGINT | - |
| 小数 | DECIMAL(p,s) | 金额等精确数值 |
| 布尔 | BOOLEAN | - |
| 时间 | TIMESTAMP | 带时区 |
| JSON | JSONB | PostgreSQL |

### 4.2 避免使用

- FLOAT / DOUBLE（精度问题）
- CHAR（除非定长）
- ENUM（扩展性差）

---

## 5. 索引策略

### 5.1 必建索引

- 主键索引（自动）
- 外键字段
- 常用查询条件字段
- 排序字段

### 5.2 组合索引

遵循最左前缀原则，将选择性高的字段放前面。

---

## 6. 示例表设计

### 6.1 {示例表名}

```sql
CREATE TABLE {table_name} (
    id BIGINT PRIMARY KEY,
    {field1} VARCHAR(255) NOT NULL,
    {field2} INT DEFAULT 0,
    {foreign_key}_id BIGINT REFERENCES {related_table}(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_{table}_{field1} ON {table_name}({field1});
CREATE INDEX idx_{table}_{foreign_key}_id ON {table_name}({foreign_key}_id);
```

---

## 7. 迁移规范

- 每次变更创建新的迁移文件
- 迁移文件命名：`{timestamp}_{description}.sql`
- 包含 UP 和 DOWN 两个方向
- 禁止修改已执行的迁移

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | {date} | {author} | 初始版本 |

---

_从 03_DB_CONVENTIONS_TEMPLATE.md 生成_
