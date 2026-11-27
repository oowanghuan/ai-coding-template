# 既有会话通知修复：已验证部分与尚未完成部分

本轮修复 WP-004 运维缺口，支持 OD-07 已批准的 WP-102/103。此前后台能读到评论并持久化 pending，但没有投递消费者；缺口发生在“识别待办 → 通知既有会话”，不是等待 Owner 批准。原始故障证据仍见上一轮 [Advisor 修订记录](../advisor-7221051445/README.md)。

## 实际证据

| 层次 | 结果 | 证据 |
|---|---|---|
| 原生接口实际投递 | 固定已加载的现有会话，active `turn/steer` 接口接受；通知实际进入模型输入，并由该上下文写入 received=true | [active-context-probe.json](active-context-probe.json) |
| 桥接逻辑隔离回归 | 16 项 Fake RPC 测试通过；原 broker 38 项检查通过。没有调用真实 NativeClient 或 GitHub | [隔离结果](isolated-result.json)、两套测试源码与日志 |
| 独立发现及修正 | queue/start 超时后可能再次发起同一未知写入；实际 Fake RPC 复现两次调用，修订后永不自动重发 | [初次独立检查](pre-fix-review.json)、[复现输出](pre-fix-probe.log)、`test_unknown_start_*` |
| 已部署后台 | 15:30、15:34 UTC 两次由 launchd 实际运行，均 31 条评论、pending=0、processed=0，journal 对账完成；未重放已关闭意见 | [首轮](poll-20261127T153024269284Z.json)、[下一轮](poll-20261127T153405314707Z.json)、[部署摘要](deployment.json) |

这四层不能混为一谈。当前没有新 Advisor 待办，后台这一轮没有走真实评论通知路径；原生投递探针是前台触发。不能据此宣称“新意见自动投递→接手→实际处理→回复→下一轮去重”全链已验收。加载但 idle 的原生 queue/start、物理重启、离线恢复、额度恢复也尚无真实端到端证据。

## 实现与权限边界

部署源码是 `poll.py.txt` 和 `session_delivery.py.txt` 的原字节副本，SHA-256 与后台记录一致。机器专用绑定、原始会话历史和权限配置保留在仓库外。原 LaunchAgent、15 分钟固定时点、RunAtLoad 和 poll.lock 单实例不变；部署前在同一锁内保存原版本，替换受信通知代码，没有运行候选、写候选仓库或改变执行权限。

桥只接受一个预先绑定且已加载的 thread/cwd，走已有本地 daemon Unix socket，方法白名单没有 thread/start、thread/resume、模型或权限设置。active 时使用带 expectedTurnId 的 steer；idle 时仅可启动本事件的明确 queuedSubmissionId，并要求队列只有这一项，避免假定默认排序或抢先执行用户队列。unloaded 时保留待办，不能创建新会话冒充接管。

事件按评论 ID、受审 SHA 和正文指纹持久化。通知只含固定说明、公开评论链接和指纹，不转抄外部评论中的指令。发送前写 intent；未知结果只核对队列/历史，不因未找到结果而盲重发。尤其 start_intent 即使仍能看到队列项，也不再次启动。

原生 accepted/history_confirmed 明确显示 awaiting_model_ack；接收回执是独立文件，须核对事件、client ID、正文指纹和既有上下文。接收不代表处理完成；公开回复仍经前台核查后的 outbox、精确远端 SHA 和评论回读确认。对已关闭事件不再通知或运行。

## 后续验证

下一条真实、已授权且未处理的 Advisor 事件到达时，应关联评论 ID/受审 SHA、poll run、通知 intent/原生 receipt、模型 ack、首个实际处理结果、公开回复与下一轮零重复记录。若仅停在任意一层，保留该层的准确状态，不要求 Owner 再输入“继续”，也不擅自开启新模型会话。

电脑休眠、离线或既有会话卸载时不能保证实时处理；恢复运行后读完整分页与持久化 journal 补读。原生接口来自本机已安装 daemon 的生成 schema，属于实验接口；版本变化时须重新探测和验证，不能把这台机器的已验证配置称为通用 Codex Adapter。

公开源码仅供审查本项目受信运维桥，不纳入项目安装器或候选执行目录。`source-index.json` 记录原始来源指纹；`artifact-index.json` 对公开副本逐文件校验。运行与测试数字只覆盖各自对象，不计入 WP-102/103 的 102 项回归总数。
