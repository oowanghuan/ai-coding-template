# WP-103 CLI 使用说明与 0.2.1-preview 升级：作者验证

本轮复现的问题是：安装 guide 引用了相对 `scripts/v4_local.py`，但安装器不会把 CLI 复制到目标项目。修订明确 `FRAMEWORK_ROOT` / `TARGET_ROOT`、绝对 CLI 路径和每条命令的 `--root`，覆盖计划保存在项目外、apply、inspect、升级及按升级事务 ID 回退；不增加安装运行时、网络或新迁移权限。

Guide 内容变更对应版本从 `0.2.0-preview` 增至 `0.2.1-preview`，旧安装资产保留。产品逻辑只修改 VERSION 常量。新增两项公开 CLI 回归，从目标目录调用框架绝对路径，检查空项目安装/读取/回退及陈旧计划保护后重新接入。

## 测试对象与身份

旧快照来自准确提交 `f95b03ab733fd45ed480aba162fee1943ea58c43`。新快照由同一提交导出后，仅叠加本轮 5 个文件（3 份文档、VERSION 模块、test_cli.py）。`input-manifest.json` 保存旧文件和新 overlay 指纹。并行 Runner 改动未混入本次测试。

本轮复核者同时是修订实现者，所以结果是**作者验证，独立非作者复核待完成**；不沿用此前独立身份，不自行工程验收。

## 真正跨版本的公开 CLI 旅程

两条路径均实际执行旧 CLI 安装 → 新 CLI plan-upgrade/apply → 新 CLI rollback → 两版 CLI inspect：

- 空项目使用旧 `plan-init` 安装。
- 既有 Git 项目使用旧 `plan-import` 接入，带 dirty tracked 文件、untracked 文件、自定义 AGENTS.md/CLAUDE.md。

共 **27 条真实命令、42 个跨步骤断言通过，退出码 0**。产品操作只调用公开 CLI，不使用内部 `plan(version=..., guide_bytes=...)` 替身。计划版本确为 0.2.0 → 0.2.1，新版本 guide 实际新增且字节与旧版本不同；旧 guide 和原 authority 字节保持。新版本 selection 生效，authority 中原契约引用仍为旧版本，不被静默改写。

新 CLI 回退后，新 guide 删除、旧 selection 原字节恢复、旧 guide/authority 原字节保持；新旧两版 CLI 均可 inspect 原 authority。重复 apply/rollback 不改动目标字节；既有 Git 与用户文件指纹全保持。所有 27 条命令退出 0。

## 回归和隔离

新快照 bootstrap 组 **22 测试通过、0 failure、0 error、0 skipped**，包含新增两项 CLI 测试。没有重跑无变化的其他组，也不把这 22 项称作全量产品回归。

7 个实际隔离探针通过：外部文件读、外部文件写、工作区 checkout 写、旧快照写、新快照写、网络连接均拒绝，凭证环境不存在。基于既有 A01 外层 Seatbelt 额外只读保护两个候选快照；所有候选执行在沙盒内，源码前后指纹保持。

`result.json` 记录命令/环境/时间/退出码及 harness/profile 指纹；`cross-version-result.json` 保存 42 断言、每条命令退出码与日志指纹、两条路径的产物指纹；`commands/` 保存真实输出。公开副本仅替换绝对路径，原始记录在仓库外。

这项升级验证不包含执行权限变更、真实供应商集成、生产 Runner、Worker 时间重叠或 WP 整体放行。没有提交、推送或发布本轮改动。
