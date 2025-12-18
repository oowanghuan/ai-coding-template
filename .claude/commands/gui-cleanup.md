# /gui-cleanup - 清理 GUI Session

你是一个 AI 协作开发助手。用户请求清理过期或无效的 GUI Session。

## 触发方式

用户可以通过以下方式触发：
- `/gui-cleanup`
- "清理 GUI Session"
- "清理僵尸连接"

## 功能说明

此命令扫描并清理以下类型的 Session：
1. **僵尸 Session**: CLI 进程已退出但文件未删除
2. **陈旧 Session**: 心跳超时超过 5 分钟
3. **过期 Session**: 超过 24 小时未活跃

## 执行步骤

### 1. 扫描 Session 目录

扫描 `.claude/gui-sessions/` 目录下的所有 Session 文件。

### 2. 检测 Session 状态

对每个 Session 执行以下检查：

| 检查项 | 条件 | 结果 |
|--------|------|------|
| 进程存活 | `kill -0 {pid}` | 存活/已退出 |
| 心跳超时 | `heartbeatAt` > 60s | 正常/陈旧 |
| 状态字段 | `status` | active/stale/disconnected |
| 最后活跃 | `lastActiveAt` > 24h | 正常/过期 |

### 3. 分类显示

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧹 GUI Session 清理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
扫描目录: .claude/gui-sessions/

📊 扫描结果:
• 活跃 Session: 2
• 陈旧 Session: 1
• 僵尸 Session: 2
• 过期 Session: 1

🔍 详细信息:

活跃 (保留):
  ● session-abc123  Terminal    15:00  PID: 12345

陈旧 (待清理):
  ⚠ session-def456  VS Code     14:30  心跳超时 8 分钟

僵尸 (待清理):
  ✗ session-ghi789  Console     昨天   进程已退出
  ✗ session-jkl012  Terminal    昨天   进程已退出

过期 (待清理):
  ○ session-mno345  Unknown     3 天前  超过 24 小时
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. 确认清理

```
是否清理 4 个无效 Session？[Y/n]
```

### 5. 执行清理

删除以下文件：
- `session-{id}.json` - Session 元信息
- `session-{id}.cmd` - 命令文件
- `session-{id}.ack` - ACK 确认文件
- `session-{id}.result` - 执行结果文件

### 6. 显示结果

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 清理完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
已删除: 4 个 Session
已保留: 2 个活跃 Session
释放空间: 12 KB

💡 提示：
• 活跃 Session 不会被清理
• 使用 /gui-disconnect 主动断开当前连接
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 参数选项

| 参数 | 说明 |
|------|------|
| `--force` | 跳过确认，直接清理 |
| `--all` | 清理所有 Session（包括活跃的，危险操作） |
| `--dry-run` | 仅显示将要清理的内容，不实际删除 |

## 自动清理策略

GUI 应用启动时会自动执行以下清理：
- 删除 `disconnected` 状态超过 24 小时的 Session
- 删除心跳超时超过 5 分钟且进程已退出的 Session

## 注意事项

- 不会清理当前终端的 Session
- 不会清理仍有活跃进程的 Session
- 清理操作不可撤销
- 建议定期执行以保持 Session 列表整洁
