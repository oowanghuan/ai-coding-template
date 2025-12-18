# /gui-disconnect - 断开 GUI 连接

你是一个 AI 协作开发助手。用户请求断开与 Coding GUI 的连接。

## 触发方式

用户可以通过以下方式触发：
- `/gui-disconnect`
- "断开 GUI"
- "关闭 GUI 连接"

## 功能说明

此命令将当前 CLI 终端从 GUI Session 列表中移除，停止接收 GUI 命令。

## 执行步骤

### 1. 检查连接状态

检查当前终端是否有活跃的 GUI Session。

如果没有连接：
```
⚠️ 当前终端未连接到 GUI

💡 提示：使用 /gui-connect 建立连接
```

### 2. 更新 Session 状态

将 Session 文件中的 `status` 字段更新为 `disconnected`：

```json
{
  "status": "disconnected",
  "lastActiveAt": "{当前时间}"
}
```

### 3. 停止监听机制

- 停止文件监听（fs.watch）
- 停止心跳更新（clearInterval）

### 4. 可选：删除 Session 文件

询问用户是否删除 Session 文件：

```
是否删除 Session 文件？[Y/n]
```

- 选择 Y：删除 `.claude/gui-sessions/session-{id}.*` 所有相关文件
- 选择 n：保留文件，GUI 会显示为"已断开"状态

### 5. 显示断开信息

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 GUI 连接已断开
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session ID: {id}
状态: ○ 已断开
持续时间: {duration}

💡 提示：
• 使用 /gui-connect 重新建立连接
• 使用 /gui-cleanup 清理所有过期 Session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 自动断开场景

以下场景会自动触发断开：

1. **终端关闭**: 进程退出时自动清理
2. **心跳超时**: 超过 60 秒未更新心跳
3. **项目切换**: 切换到不同项目目录

## 注意事项

- 断开后 GUI 会立即感知到状态变化
- 未删除的 Session 文件会在 24 小时后自动清理
- 断开不会影响 CLI 的其他功能
