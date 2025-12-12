# schema_generator - 生成数据库 Schema

## 能力描述

根据 `10_DESIGN_FINAL.md` 中定义的数据模型，自动生成数据库 Schema。支持多种 ORM/数据库格式。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| format | string | 否 | 输出格式：`prisma`（默认）, `typeorm`, `sql`, `mongoose` |
| output_path | string | 否 | 输出路径，默认根据 format 自动确定 |

## 输出

- 数据库 Schema 文件
- 迁移文件（如适用）

## 执行步骤

### 1. 读取数据模型定义

```markdown
# 从 docs/{feature}/10_DESIGN_FINAL.md 提取

## 数据模型

### User

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | number | 是 | 主键，自增 |
| email | string | 是 | 邮箱，唯一索引 |
| password | string | 是 | 密码哈希 |
| name | string | 是 | 用户名 |
| avatar | string | 否 | 头像 URL |
| status | enum | 是 | 状态：active/inactive/banned |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |

### Token

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | number | 是 | 主键 |
| token | string | 是 | Token 值，唯一 |
| user_id | number | 是 | 关联用户，外键 |
| type | enum | 是 | 类型：access/refresh |
| expires_at | datetime | 是 | 过期时间 |
```

### 2. 解析模型关系

```yaml
models:
  User:
    fields:
      - name: id
        type: Int
        attributes: [@id, @default(autoincrement())]
      - name: email
        type: String
        attributes: [@unique]
      # ...
    relations:
      - name: tokens
        type: Token[]
        relation: one-to-many

  Token:
    fields:
      # ...
    relations:
      - name: user
        type: User
        relation: many-to-one
        foreign_key: user_id
```

### 3. 生成 Schema

#### Prisma 格式

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum UserStatus {
  active
  inactive
  banned
}

enum TokenType {
  access
  refresh
}

model User {
  id        Int        @id @default(autoincrement())
  email     String     @unique
  password  String
  name      String
  avatar    String?
  status    UserStatus @default(active)
  createdAt DateTime   @default(now()) @map("created_at")
  updatedAt DateTime   @updatedAt @map("updated_at")

  tokens    Token[]

  @@map("users")
}

model Token {
  id        Int       @id @default(autoincrement())
  token     String    @unique
  userId    Int       @map("user_id")
  type      TokenType
  expiresAt DateTime  @map("expires_at")
  createdAt DateTime  @default(now()) @map("created_at")

  user      User      @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@map("tokens")
}
```

#### TypeORM 格式

```typescript
// src/entities/user.entity.ts

import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, OneToMany } from 'typeorm'
import { Token } from './token.entity'

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  BANNED = 'banned'
}

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number

  @Column({ unique: true })
  email: string

  @Column()
  password: string

  @Column()
  name: string

  @Column({ nullable: true })
  avatar: string

  @Column({ type: 'enum', enum: UserStatus, default: UserStatus.ACTIVE })
  status: UserStatus

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date

  @OneToMany(() => Token, token => token.user)
  tokens: Token[]
}
```

#### SQL 格式

```sql
-- migrations/001_create_users.sql

CREATE TYPE user_status AS ENUM ('active', 'inactive', 'banned');
CREATE TYPE token_type AS ENUM ('access', 'refresh');

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  avatar VARCHAR(255),
  status user_status DEFAULT 'active' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE tokens (
  id SERIAL PRIMARY KEY,
  token VARCHAR(255) UNIQUE NOT NULL,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type token_type NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_tokens_user_id ON tokens(user_id);
```

### 4. 输出结果

```
✅ Schema 生成成功

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 生成摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
格式：Prisma
模型数量：2
枚举数量：2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 生成的文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ prisma/schema.prisma

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 模型详情
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• User (8 字段, 1 关系)
• Token (6 字段, 1 关系)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 下一步：
1. 检查生成的 Schema 是否符合预期
2. 运行 npx prisma db push 应用到数据库
3. 运行 npx prisma generate 生成客户端
```

## 示例

### 示例 1：生成 Prisma Schema

```
请使用 schema_generator skill：
- feature: user-auth
- format: prisma
```

### 示例 2：生成 SQL 迁移

```
请使用 schema_generator skill：
- feature: user-auth
- format: sql
- output_path: migrations/
```

## 注意事项

1. **命名约定**：遵循 `03_DB_CONVENTIONS.md` 中的命名规则
2. **关系推断**：自动推断一对多、多对多关系
3. **索引优化**：为外键和常用查询字段添加索引
4. **枚举处理**：自动识别枚举类型并生成对应定义
5. **增量更新**：支持追加新模型，不影响已有定义

## 关联工具

- `design_from_demo` - 从 Mock API 推导数据模型
- `/gen-demo` - 生成 Demo 时参考数据模型
- `review_alignment` - 验证实现与 Schema 一致性
