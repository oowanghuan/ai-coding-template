# openai_expert_review - OpenAI API 评审执行器

## 能力描述

作为 Expert Reviewer 的执行器（Runner），负责调用 OpenAI API 执行评审。

**职责边界**：
- ✅ 管理 OPENAI_API_KEY
- ✅ 执行 OpenAI API 调用
- ✅ 处理超时、重试、错误
- ❌ **不定义评审规则**（由 Agent 定义）
- ❌ **不解析业务语义**（只返回原始响应）

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 评审 Prompt 内容 |
| model | string | 否 | 模型名称，默认 `gpt-4.1` |
| temperature | number | 否 | 温度，默认 `0.3` |
| max_tokens | number | 否 | 最大 tokens，默认 `4096` |

## 输出

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| content | string | API 响应内容（成功时） |
| error | string | 错误信息（失败时） |
| usage | object | Token 使用统计 |

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key | **必需** |
| `EXPERT_REVIEW_MODEL` | 使用的模型 | `gpt-4.1` |
| `EXPERT_REVIEW_TIMEOUT` | 超时时间（秒） | `60` |
| `EXPERT_REVIEW_MAX_RETRIES` | 最大重试次数 | `3` |

### 配置检查

在执行前，检查 API Key：

```bash
# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: OPENAI_API_KEY 未配置"
  exit 1
fi
```

## 执行方式

### 方式 1：使用 curl 命令

```bash
curl -s -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "'"${model:-gpt-4.1}"'",
    "messages": [
      {
        "role": "system",
        "content": "You are an expert code reviewer. Always respond in the exact YAML format specified."
      },
      {
        "role": "user",
        "content": "'"$(echo "$prompt" | jq -Rs .)"'"
      }
    ],
    "temperature": '"${temperature:-0.3}"',
    "max_tokens": '"${max_tokens:-4096}"'
  }'
```

### 方式 2：使用 Python 脚本

如果 curl 不方便处理复杂 prompt，可使用 Python：

```python
#!/usr/bin/env python3
import os
import json
import sys
from openai import OpenAI

def call_openai(prompt, model="gpt-4.1", temperature=0.3, max_tokens=4096):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"success": False, "error": "OPENAI_API_KEY not configured"}

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer. Always respond in the exact YAML format specified."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "success": True,
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    prompt = sys.stdin.read()
    result = call_openai(prompt)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 执行步骤

### 1. 验证 API Key

```
检查 OPENAI_API_KEY 环境变量是否存在
如果不存在：返回错误 ERR_API_KEY_MISSING
```

### 2. 准备请求

```
构建 API 请求体：
- model: 从参数或环境变量获取
- messages: 构建 system + user 消息
- temperature: 默认 0.3（低随机性）
- max_tokens: 默认 4096
```

### 3. 执行 API 调用

```
发送 POST 请求到 OpenAI API
超时设置：60 秒（可配置）

如果失败，进行重试：
- 最多重试 3 次
- 重试间隔：1s, 2s, 4s（指数退避）
```

### 4. 处理响应

```
如果成功：
  提取 choices[0].message.content
  返回 {success: true, content: ..., usage: ...}

如果失败：
  返回 {success: false, error: ...}
```

## 错误处理

| 错误类型 | HTTP 状态 | 处理方式 |
|---------|----------|----------|
| API Key 无效 | 401 | 提示用户检查 Key |
| 配额不足 | 429 | 提示用户检查配额 |
| 模型不可用 | 404 | 提示用户检查模型名 |
| 超时 | - | 重试（最多 3 次） |
| 网络错误 | - | 重试（最多 3 次） |
| 响应格式错误 | - | 返回原始响应，提示人工检查 |

## 使用示例

### 在 expert_reviewer 中调用

```markdown
调用 openai_expert_review skill：
- prompt: {构建的评审 Prompt}
- model: gpt-4.1
- temperature: 0.3
- max_tokens: 4096

等待返回结果...

如果 success == true：
  从 content 中提取 YAML 块
  解析并验证格式

如果 success == false：
  根据 error 类型提示用户
```

### 直接使用 Bash 调用

```bash
# 设置环境变量
export OPENAI_API_KEY="sk-..."

# 准备 prompt（保存到临时文件）
cat > /tmp/prompt.txt << 'EOF'
你是一个独立的第三方专家评审员...
（完整 prompt 内容）
EOF

# 调用 API
PROMPT=$(cat /tmp/prompt.txt)
MODEL=${EXPERT_REVIEW_MODEL:-gpt-4.1}

RESPONSE=$(curl -s -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --max-time 60 \
  -d "$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    '{
      model: $model,
      messages: [
        {role: "system", content: "You are an expert code reviewer. Always respond in the exact YAML format specified."},
        {role: "user", content: $prompt}
      ],
      temperature: 0.3,
      max_tokens: 4096
    }')")

# 提取内容
echo "$RESPONSE" | jq -r '.choices[0].message.content'
```

## 成本估算

| 模型 | 输入价格 | 输出价格 | 典型评审成本 |
|------|---------|---------|-------------|
| gpt-4.1 | $2/1M tokens | $8/1M tokens | ~$0.05-0.10 |
| gpt-4o | $5/1M tokens | $15/1M tokens | ~$0.10-0.20 |

**建议**：
- 开发测试时使用 `--dry-run` 模式
- 生产评审使用 gpt-4.1（性价比最优）

## 安全注意事项

1. **API Key 保护**：不要在代码中硬编码 API Key
2. **敏感信息过滤**：不要将 .env、credentials 等文件内容发送到 API
3. **日志脱敏**：不要在日志中输出完整的 API Key

## 关联工具

- `expert_reviewer` - 调用此 skill 的 Subagent
- `/expert-review` - 用户入口命令
