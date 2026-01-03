# 03_EXTERNAL_API_CONVENTIONS.md
# 外部 API 调用规范

> 版本：v1.0
> 最后更新：{timestamp}
> 适用范围：所有外部 API 调用（OpenAI、第三方服务等）

---

## 1. 概述

本文档定义项目中调用外部 API 的规范，确保：
- API 调用安全可控
- 错误处理标准化
- 重试机制一致
- 便于 Claude Code 生成符合规范的调用代码

---

## 2. API 分类

### 2.1 按用途分类

| 类型 | 描述 | 示例 |
|------|------|------|
| AI 服务 | LLM、图像生成等 AI 能力 | OpenAI, Claude, Gemini |
| 基础设施 | 云服务、存储、CDN | AWS, Supabase, Vercel |
| 第三方业务 | 支付、通知、认证 | Stripe, SendGrid, Auth0 |
| 数据服务 | 数据查询、分析 | Elasticsearch, Analytics |

### 2.2 按调用模式分类

| 模式 | 特征 | 处理方式 |
|------|------|----------|
| 同步调用 | 立即返回结果 | await / .then() |
| 异步回调 | Webhook 通知结果 | 回调处理器 |
| 轮询 | 定期查询状态 | 定时器 + 状态检查 |
| 流式 | 流式返回数据 | Stream 处理 |

---

## 3. 配置管理

### 3.1 环境变量命名

```bash
# 格式：{SERVICE}_{TYPE}_{PURPOSE}

# API Keys
OPENAI_API_KEY=sk-xxx
SUPABASE_SERVICE_KEY=xxx
STRIPE_SECRET_KEY=sk_live_xxx

# Endpoints（非必须，有默认值时可省略）
OPENAI_API_BASE=https://api.openai.com/v1
SUPABASE_URL=https://xxx.supabase.co

# Feature Flags
OPENAI_ENABLED=true
STRIPE_TEST_MODE=false
```

### 3.2 配置文件结构

```typescript
// config/external-api.ts
interface ExternalAPIConfig {
  openai: {
    apiKey: string;           // 从 OPENAI_API_KEY 读取
    apiBase?: string;         // 可选，默认官方 endpoint
    defaultModel: string;     // 默认模型
    maxTokens: number;        // 默认最大 token
    timeout: number;          // 超时时间 (ms)
    maxRetries: number;       // 最大重试次数
  };
  // ... 其他服务配置
}
```

### 3.3 敏感信息保护

```
# ❌ 禁止
- 在代码中硬编码 API Key
- 在日志中输出完整 Key
- 在错误消息中暴露 Key
- 在 Git 中提交 .env 文件

# ✅ 必须
- 从环境变量读取 Key
- 日志中 Key 脱敏（显示前4后4位）
- .env 加入 .gitignore
- 使用 secrets 管理工具（生产环境）
```

---

## 4. 调用规范

### 4.1 标准调用结构

```typescript
interface APICallOptions<TRequest, TResponse> {
  // 请求配置
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: TRequest;
  timeout?: number;

  // 重试配置
  maxRetries?: number;
  retryDelay?: number;
  retryableErrors?: string[];

  // 响应处理
  validateResponse?: (res: TResponse) => boolean;
  transformResponse?: (res: any) => TResponse;
}
```

### 4.2 请求头规范

```typescript
// 标准请求头
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${apiKey}`,
  'User-Agent': 'ProjectName/1.0',       // 标识调用来源
  'X-Request-ID': generateRequestId(),   // 请求追踪 ID
};
```

### 4.3 超时设置

| API 类型 | 推荐超时 | 说明 |
|----------|----------|------|
| LLM 推理 | 60-120s | 长文本生成需要更长时间 |
| 图像生成 | 120-180s | 图像生成耗时较长 |
| 数据查询 | 10-30s | 数据库查询 |
| 通用 REST | 5-10s | 一般 CRUD 操作 |

---

## 5. 错误处理

### 5.1 错误分类

| 类型 | HTTP 状态码 | 处理方式 |
|------|-------------|----------|
| 客户端错误 | 400-499 | 不重试，修复请求 |
| 速率限制 | 429 | 指数退避重试 |
| 服务端错误 | 500-599 | 重试 |
| 网络错误 | - | 重试 |
| 超时 | - | 重试 |

### 5.2 可重试错误

```typescript
const RETRYABLE_ERRORS = [
  'ETIMEDOUT',           // 超时
  'ECONNRESET',          // 连接重置
  'ECONNREFUSED',        // 连接拒绝
  'RATE_LIMIT_EXCEEDED', // 速率限制
  'SERVICE_UNAVAILABLE', // 服务不可用
];

const RETRYABLE_STATUS_CODES = [
  429,  // Too Many Requests
  500,  // Internal Server Error
  502,  // Bad Gateway
  503,  // Service Unavailable
  504,  // Gateway Timeout
];
```

### 5.3 重试策略

```typescript
interface RetryConfig {
  maxRetries: number;        // 最大重试次数，默认 3
  initialDelay: number;      // 初始延迟 (ms)，默认 1000
  maxDelay: number;          // 最大延迟 (ms)，默认 30000
  backoffMultiplier: number; // 退避乘数，默认 2
  jitter: boolean;           // 是否添加随机抖动，默认 true
}

// 延迟计算公式
// delay = min(initialDelay * (backoffMultiplier ^ attempt), maxDelay)
// if jitter: delay = delay * (0.5 + random() * 0.5)
```

### 5.4 错误响应标准化

```typescript
interface ExternalAPIError {
  // 错误标识
  code: string;              // 内部错误码
  externalCode?: string;     // 外部 API 错误码

  // 错误信息
  message: string;           // 用户可见消息
  details?: any;             // 详细信息

  // 上下文
  service: string;           // 服务名称
  endpoint: string;          // 调用端点
  requestId?: string;        // 请求 ID

  // 元数据
  statusCode?: number;       // HTTP 状态码
  retryable: boolean;        // 是否可重试
  timestamp: string;         // 错误发生时间
}
```

---

## 6. OpenAI API 特定规范

### 6.1 调用配置

```typescript
interface OpenAIConfig {
  apiKey: string;
  model: 'gpt-4.1' | 'gpt-4' | 'gpt-3.5-turbo';
  maxTokens: number;          // 默认 4096
  temperature: number;        // 默认 0.7，评审场景用 0.3
  timeout: number;            // 默认 60000ms
  maxRetries: number;         // 默认 3
}
```

### 6.2 Prompt 构建规范

```typescript
interface PromptTemplate {
  system: string;             // 系统提示词
  user: string;               // 用户提示词
  variables: Record<string, string>;  // 模板变量
}

// 模板示例
const reviewPrompt: PromptTemplate = {
  system: `你是一个独立的第三方专家评审员。
你的职责是评审 AI 协作开发项目中的设计文档。

## 评审原则
1. 独立性：必须客观公正
2. 可执行性：每个问题必须有明确修复建议
...`,
  user: `## 被评审文档

{document_content}

## 输出格式
请严格按照以下 YAML 格式输出...`,
  variables: {
    document_content: '',  // 运行时填充
  }
};
```

### 6.3 响应解析

```typescript
// 从 OpenAI 响应中提取结构化数据
function parseOpenAIResponse<T>(response: string): T {
  // 1. 尝试提取 YAML/JSON 代码块
  const yamlMatch = response.match(/```yaml\n([\s\S]*?)\n```/);
  const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/);

  // 2. 解析提取的内容
  if (yamlMatch) {
    return parseYaml(yamlMatch[1]);
  }
  if (jsonMatch) {
    return JSON.parse(jsonMatch[1]);
  }

  // 3. 尝试直接解析整个响应
  try {
    return parseYaml(response);
  } catch {
    throw new Error('ERR_PARSE_RESPONSE');
  }
}
```

---

## 7. 日志规范

### 7.1 请求日志

```typescript
// 请求开始
logger.info('external_api_request', {
  service: 'openai',
  endpoint: '/v1/chat/completions',
  requestId: 'req-abc123',
  model: 'gpt-4.1',
  // 不记录敏感数据（API Key、完整请求体）
});

// 请求完成
logger.info('external_api_response', {
  service: 'openai',
  requestId: 'req-abc123',
  statusCode: 200,
  duration: 1234,  // ms
  tokens: { prompt: 100, completion: 200 },
});
```

### 7.2 错误日志

```typescript
logger.error('external_api_error', {
  service: 'openai',
  requestId: 'req-abc123',
  errorCode: 'RATE_LIMIT_EXCEEDED',
  statusCode: 429,
  retryAttempt: 2,
  nextRetryIn: 4000,  // ms
  // 不记录完整错误响应（可能包含敏感信息）
});
```

### 7.3 脱敏规则

```typescript
// API Key 脱敏
function maskApiKey(key: string): string {
  if (key.length <= 8) return '****';
  return key.slice(0, 4) + '****' + key.slice(-4);
}

// 输出示例
// sk-abc1****xyz9
```

---

## 8. 测试规范

### 8.1 Mock 策略

```typescript
// 开发环境使用 Mock
if (process.env.NODE_ENV === 'development') {
  // 使用 MSW 或类似工具 mock API
}

// 测试环境使用固定响应
if (process.env.NODE_ENV === 'test') {
  // 使用 jest.mock 或类似机制
}
```

### 8.2 Mock 响应示例

```typescript
const mockOpenAIResponse = {
  id: 'chatcmpl-mock123',
  object: 'chat.completion',
  created: 1702627200,
  model: 'gpt-4.1',
  choices: [{
    index: 0,
    message: {
      role: 'assistant',
      content: '```yaml\nverdict: GO\nsummary:\n  total_issues: 0\n```'
    },
    finish_reason: 'stop'
  }],
  usage: {
    prompt_tokens: 100,
    completion_tokens: 50,
    total_tokens: 150
  }
};
```

---

## 9. 监控与告警

### 9.1 监控指标

| 指标 | 描述 | 告警阈值 |
|------|------|----------|
| 请求延迟 | P99 响应时间 | > 30s |
| 错误率 | 5xx 错误比例 | > 5% |
| 重试率 | 触发重试的请求比例 | > 20% |
| 速率限制 | 429 响应比例 | > 10% |

### 9.2 告警配置

```yaml
# 告警规则示例
alerts:
  - name: openai_high_latency
    condition: "p99_latency > 30000"
    severity: warning
    action: notify_slack

  - name: openai_high_error_rate
    condition: "error_rate > 0.05"
    severity: critical
    action: notify_pagerduty
```

---

## 10. Claude Code 使用指南

### 10.1 生成 API 调用代码时的检查清单

- [ ] API Key 是否从环境变量读取
- [ ] 是否设置了合理的超时时间
- [ ] 是否实现了重试机制
- [ ] 是否处理了所有错误类型
- [ ] 是否有请求/响应日志
- [ ] 敏感信息是否脱敏

### 10.2 代码模板

```typescript
// 标准 API 调用模板
async function callExternalAPI<TReq, TRes>(
  config: APICallOptions<TReq, TRes>
): Promise<TRes> {
  const {
    endpoint, method, body,
    maxRetries = 3,
    timeout = 30000
  } = config;

  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(endpoint, {
        method,
        headers: config.headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: AbortSignal.timeout(timeout),
      });

      if (!response.ok) {
        throw new ExternalAPIError({
          code: 'API_ERROR',
          statusCode: response.status,
          retryable: RETRYABLE_STATUS_CODES.includes(response.status),
        });
      }

      return await response.json();
    } catch (error) {
      lastError = error;

      if (!isRetryable(error) || attempt === maxRetries) {
        throw error;
      }

      await delay(calculateBackoff(attempt));
    }
  }

  throw lastError;
}
```

---

## 附录：服务配置速查

### A. OpenAI

```typescript
{
  endpoint: 'https://api.openai.com/v1/chat/completions',
  authHeader: 'Authorization: Bearer {OPENAI_API_KEY}',
  timeout: 60000,
  maxRetries: 3,
}
```

### B. Supabase

```typescript
{
  endpoint: '{SUPABASE_URL}/rest/v1',
  authHeader: 'apikey: {SUPABASE_ANON_KEY}',
  timeout: 10000,
  maxRetries: 2,
}
```

---

## 模板使用说明

1. 复制此文件到 `docs/_foundation/_api_system/03_EXTERNAL_API_CONVENTIONS.md`
2. 替换 `{timestamp}` 为当前日期
3. 根据项目实际使用的外部服务调整配置
4. 删除此"模板使用说明"段落
