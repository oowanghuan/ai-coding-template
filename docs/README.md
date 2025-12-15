# docs 目录 - 功能文档中心

此目录存放所有功能模块的文档，按照 8 阶段工作流组织。

## 目录结构

```
docs/
├── _foundation/              # 项目级基础配置
│   ├── 01_PROJECT_PROFILE.yaml    # 项目画像
│   ├── 02_API_CONVENTIONS.md      # API 规范
│   ├── 03_DB_CONVENTIONS.md       # DB 规范
│   └── _ui_system/                # UI 设计系统
│
├── {feature-name}/           # 功能模块文档
│   ├── 10_CONTEXT.md              # 功能上下文
│   ├── 40_DESIGN.md               # 技术设计
│   ├── 21_UI_FLOW_SPEC.md         # UI 规格
│   ├── 20_API_SPEC.md             # API 规格
│   ├── 90_PROGRESS_LOG.yaml       # 进度日志
│   ├── 91_DAILY_SUMMARY/          # 每日总结
│   ├── 60_TEST_PLAN.md            # 测试计划
│   └── 70_RELEASE_NOTE.md         # 发布说明
│
└── README.md                 # 本文件
```

## 文档编号规则

| 前缀 | 阶段 | 文档类型 |
|------|------|----------|
| 00 | Phase 0/1 | 上下文 (Context) |
| 01 | Phase 0 | 项目配置 (Profile) |
| 10 | Phase 4 | 详细设计 (Design) |
| 11 | Phase 2 | 规格定义 (Spec) |
| 20 | Phase 5 | 开发计划 (Dev Plan) |
| 30 | Phase 5 | 进度日志 |
| 40 | Phase 6 | 测试文档 |
| 50 | Phase 7 | 发布文档 |

## 创建新功能

使用 Claude Code 命令快速创建功能目录：

```bash
# 在 Claude Code 中执行
/new-feature my-feature-name
```

这会自动生成包含所有模板的功能目录。

## 文档模板位置

所有模板定义在 `_templates/CC_COLLABORATION/03_TEMPLATES/` 目录中。

---

_由 AI 协作开发框架生成_
