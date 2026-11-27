# #3 本机轮询断点、修复与两次后台运行

日期：2026-11-27 UTC。对象：Advisor 评论 [7203311332](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7203311332)，原受审 SHA `6efbc7525416f36963000e45029c6e3ce6403273`。本记录不代表 V4 S10/S11 完整产品验收或阶段放行。

## 现场与第一个断点

修复前已在仓库外复制轮询器目录、全部 runs、日志、配置和文件指纹；先读取 launchctl，确认当时任务空闲、累计运行 33 次、最后退出 1，再暂时卸载任务进行修复。没有删除旧日志或 journal。

最后调度 `2026-11-27T04:52:00.254123Z` → 读到 3 条评论 → pending=1 → 第一个 `git fetch` 退出 128：`fatal: Unable to read current working directory: Operation not permitted`。首次同样失败出现在 `2026-11-26T21:02:50.854633Z`。原运行器将 subprocess 的默认 cwd 指向 Desktop 中的前台仓库；launchd 后台进程读评论不需访问仓库，但 Git 必须访问该目录，因此直到有 pending 才暴露访问限制。

这是实际观测到的后台 Desktop 访问失败；没有修改系统隐私权限去绕过它，也未把单凭错误文本推断出的具体 TCC 规则当作已证实。对账确认：前台工作树干净、无额外 Worktree、无 operation journal、本地/远端设计分支一致，没有待保全的修订或未知写入。完整失败记录见 [last-failure.json](last-failure.json)。

原先无 pending 的调度成功和只读模型唤起只覆盖了前半段，不能证明真正意见处理路径可用。这是首次接入验证遗漏，现已补真实后台请求处理。

## A01 边界与修复

当前运行器移除 Desktop/local Git 依赖、模型执行、候选脚本执行、commit 和 push。唯一子进程是固定 GH broker；接口限制为身份/本 Issue/远端设计分支/提交比较的读取，以及本 Issue 评论追加；使用最小环境变量名单。候选内容没有可执行入口，也不会继承 broker 的发布认证。未关闭沙盒、未增加权限、未创建付费服务。

前台 Project Lead 核查内容后生成仓库外 outbox，绑定 Advisor 正文指纹、评论 ID、受审 SHA、预期远端 HEAD、回复指纹和处理结局。后台再次读回核对后才追加文字。outbox 是可信运维输入，不能从候选仓库自动生成或执行；新意见无 outbox 时保持 pending，后续由 Project Lead 在已有范围处理。此限制明确牺牲无人值守模型整改，尚未提供无发布权限的候选执行沙盒。

[runner.py.txt](runner.py.txt) 是本次实际安装文件的逐字节快照，无机器私有路径；SHA256 为 `e02468ddcdbd037bd14f597308339da088f34644ddfcecfa434eed7aa50a6fd5`。历史原始快照保留在上级目录和原提交中，不用新实现覆写旧证据。

## 两次真实后台运行

| 运行 | 触发/起止时间 UTC | 评论 / pending / processed | 结果 |
|---|---|---|---|
| [第一次](first-background.json) | launchd bootstrap 的 RunAtLoad；05:04:59.693427–05:05:12.499733 | 3 / 1 / 1 | 固定 broker 实际追加评论 7210336111，读回成功；journal published |
| [第二次](second-background.json) | 对同一已注册任务执行 launchctl kickstart；05:05:39.401532–05:05:46.394972 | 4 / 0 / 0 | 重新读全部评论及远端，完成 journal 对账，无再次发布 |

两次都由实际 LaunchAgent 执行，不是前台直接运行 Python。第二次是显式触发下一轮，没有等待 15 分钟，不能称作两个自然定时间隔。原 900 秒配置仍保持；[调度摘要](scheduler.json)记录 reload 后 runs=2、last exit=0。完整步骤和时间戳见各 result 文件。

处理结果：[评论 7210336111](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7210336111)。[journal-receipt.json](journal-receipt.json)记录评论 ID、原受审 SHA、operation key、回复指纹和运行 ID。第二次补读按同一键去重，不靠内存游标；本条处理进展不是对 A01–A03 的最终验收关闭。

## A02 终止、对账与负向验证

- GO 无待办：前台确认后以 closed 意见处理回复收口，不发新请复核；后续补读为 pending=0。
- 异议/补证：确有待复核内容时才选择 needs_review，并绑定新证据/SHA；needs_owner 仅用于真正需决定的范围/放行，普通进展为 result。
- 旧 push 成功、缺评论：从远端相同 SHA 或 compare 的祖先关系确认，转 push_confirmed；只允许继续已核查的文字，绝不重做 push/代码。未确认 push 或结果未知且看不到回执的 POST 保持冻结。已看到操作键对应评论则恢复 published，即使本地 receipt 丢失。

[negative-checks.json](negative-checks.json)的 23 项合成检查，包括候选脚本不执行、固定子进程/端点、凭证环境过滤、输入/HEAD 篡改拒绝、GO 终止、旧 push 对账、丢失评论回执和重复处理。脚本为 [test_restricted.py.txt](test_restricted.py.txt)。复跑可把两个快照放入独立临时目录，分别命名 poll.py 和 test_restricted.py，运行 `python3 test_restricted.py`；测试将 API 替换为合成对象，不联网、不发布、不执行候选脚本。运行器完整未知写入故障链尚无真实远端故障注入验收。

[manifest.json](manifest.json)记录公开源快照、两次运行、测试结果与 receipt 的指纹。机器休眠/离线/退出登录的边界保持不变；本轮未做物理重启、断网或云端定时运行测试。后续 Advisor 意见和普通修订仍由 Project Lead 处理，独立复核及阶段放行权限没有变化。
