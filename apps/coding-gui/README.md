# Coding GUI

> AI 协作开发的可视化工作流管理界面

一个 Electron 桌面应用，提供：
- Phase 导航和 Step 执行
- 工作流配置系统
- GUI-CLI 通信（保留完整对话上下文）

## 快速开始

```bash
# 安装依赖
npm install

# 开发模式启动
npm run dev

# 构建生产版本
npm run build
```

## 使用流程

### 1. 启动 GUI

```bash
cd apps/coding-gui
npm install
npm run dev
```

### 2. 连接 CLI

在 Claude Code 中执行：

```
/gui-connect
```

### 3. 使用 GUI 发送命令

1. 在 GUI 中打开项目
2. 点击任意执行按钮
3. GUI 显示：`命令已发送，请在 CLI 中输入"执行"并回车`
4. 在 CLI 中输入"执行"并回车
5. Claude 自动执行命令（保留完整上下文）

## 工作原理

```
GUI 点击 → 写入 .cmd 文件 → 用户输入"执行" → Hook 注入命令 → Claude 执行
```

**核心约束**：保留完整对话上下文。采用 UserPromptSubmit Hook 方案。

## 技术栈

- **Electron** - 跨平台桌面应用
- **Vue 3** - 前端框架
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **electron-vite** - 构建工具

## 目录结构

```
src/
├── main/              # Electron 主进程
│   ├── index.ts       # 入口
│   ├── ipc/           # IPC 处理器和中间件
│   └── services/      # 后端服务
├── preload/           # 预加载脚本（安全桥接）
├── renderer/          # Vue 渲染进程
│   ├── components/    # UI 组件
│   ├── composables/   # 组合式函数
│   ├── services/      # 前端服务
│   ├── stores/        # Pinia 状态
│   └── views/         # 页面视图
└── shared/            # 共享类型和常量
```

## 测试

```bash
# 单元测试
npm run test

# E2E 测试
npm run test:e2e

# 覆盖率报告
npm run test:coverage
```

## GUI-CLI 通信文件

Session 文件存储在项目的 `.claude/gui-sessions/`：

| 文件 | 作用 |
|------|------|
| `session-{id}.json` | Session 信息（CLI 创建） |
| `session-{id}.cmd` | 待执行命令（GUI 创建） |
| `session-{id}.ack` | 命令确认（Hook 创建） |
| `session-{id}.result` | 执行结果（可选） |

## 相关命令

| 命令 | 说明 |
|------|------|
| `/gui-connect` | CLI 连接 GUI |
| `/gui-disconnect` | CLI 断开连接 |
| `/gui-cleanup` | 清理会话文件 |

## License

MIT
