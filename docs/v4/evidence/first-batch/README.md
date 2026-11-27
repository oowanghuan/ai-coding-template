# WP-001 / WP-101 首批作者验证

授权：[Owner 裁定 7214229053](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7214229053)，仅 WP-001/101。设计基线 `1fbe382a2ffce858f15ba1769e3068054e589f96`；实际测试代码提交 `ee262fdb46b9aa0e6888bb761d1a9624110b545b`。后继证据提交仅补文档和快照，受审完整 SHA 见 #3 请审评论。

2026-11-27 10:09:03–10:09:22 UTC，macOS 15.5 arm64、Python 3.9.6。`results.json` 记录命令、固定依赖版本、输入指纹和返回码。`tests.stdout` / `tests.stderr` 是实际日志：安装 19 通过、协议 30 通过，失败/错误/跳过均 0，进程退出 0。运行前后测试输入指纹一致。

| 范围 | 已实测 | 尚未据此证明 |
|---|---|---|
| WP-001 | 空目录安装 52 工具 + 98 框架资源；dry-run；重复安全；已有 Git/用户文件保全；冲突提前拒绝；缺源/漂移/缺依赖；路径/符号链接；同机互斥；安全回退及未知中断文件保留 | 当前供应商原生发现、完整项目 init/import/upgrade、恶意文件系统并发替换、真实断电恢复 |
| WP-101 | Schema、唯一 ID/引用、依赖环/版本、授权/预算/暂停、Assignment/Session/范围、租约声明、未知操作、独立性声明、类型里程碑、状态迁移、契约修改失效签认等反例 | 身份和授权真实性、可信执行证据 Gate、真正排他认领/fencing、可恢复存储、真实双 CLI/多机、业务价值 |
| A01 | 剥离凭证环境变量；禁止隔离目录外的无敏感 canary 读取/写入、仓库写入和网络连接 | 完整主机安全审计或对所有 OS 攻击面的证明 |
| 本机运维 | 27 项受限 broker 回归检查；Owner 裁定事件识别与已有回复去重；自然后台读回记录 | 无人值守模型整改、云端实际调度配置、物理重启/休眠/离线恢复 |

隔离入口为系统 `sandbox-exec`；候选与其子进程仅能写临时夹，不继承 GitHub/API/SSH 环境凭证。仅允许系统运行库、公开工作树和已安装 Python 依赖读取；不允许网络，未授予 securityd 查询。候选运行后，前台通过独立 Git 步骤提交；候选进程不能推送。`sandbox.sb.txt` 是路径替换后的实际策略，`run_tests.py.txt` 是实际驱动源码；原始与公开策略指纹分别记录，不能混为同一字节对象。

复跑时由验证者在自己的隔离环境配置 `<workspace>`、`<python-dependencies>`、`<isolated-run>`，准备只包含 `base/repo/deps/canary` 路径的 `config.json`；canary 应放在允许目录之外且不含敏感信息。设临时 HOME/TMPDIR，使用 `env -i` 等价白名单、`PYTHONNOUSERSITE=1`、`PYTHONDONTWRITEBYTECODE=1`，以 `python3 -B -S` 启动该驱动。先验隔离负向检查，再执行两个测试目录。测试本身也可由已有安全 CI 使用 `python3 -m unittest discover -s tests/install -v` 和 `python3 -m unittest discover -s tests/protocol -v`，不要让未审候选继承发布凭证。

保留失败史：首次隔离环境因没有允许读取根目录本身而未能启动无害程序，未运行候选；添加根目录本身读取后启动成功。首轮测试驱动复用 unittest loader，安装 16 项通过后协议组未启动，退出 1；见 `initial-harness.*`。修正驱动并增加边界用例后得到本次 49 项通过；没有将早期未运行计作通过。

原版 P0 审计和设计检查固定于旧源码，故其历史证据保留在原目录，不在已修复源码上冒充同一基线重跑。五份被修改的旧原件与 V3 Git 对象逐字节一致，见 `preserved-originals.json`。本批只完成组件自测，S01–S12 的完整 V4 产品验收没有因此变成 passed。独立 Advisor 签认 pending。

## 本机漏接裁定的根因

旧匹配器只识别 `[Advisor · 评审]`，且要求引用已有请审。09:40 实际读到 16 条但 pending=0；Owner 裁定 7214229053 属 `[Advisor · Owner 裁定转记]`，被错误遗漏。修复将已识别 Owner 账号的裁定独立分类，无 SHA 时记为待核查 unbound，不自动授予权限；前台核对后以评论 7215024908 接收。

`poll-after-fix.json` 为 09:55 自然运行；`poll-next-natural.json` 为 10:10 的下一次自然运行。两次均读到 17 条、识别裁定 1、pending=0、processed=0；已有接收回执正确去重。`poll.py.txt` 是修复后源快照，`test_poll.py.txt` / `poll-tests.json` 为 27 项实际隔离回归。后台仍只读核查与发送已核查文字；未恢复候选执行或模型唤起。

本机固定分钟为每小时 :10/:25/:40/:55，保留登录启动和单实例锁；这避免重载后相位漂移，但不能消除长时间评审刚好跨过读取点的等待。云端固定分钟仍待对端确认，不把双端完全对齐记为已验证。电脑休眠、离线或未登录时无法保证本机执行，恢复后补读。
