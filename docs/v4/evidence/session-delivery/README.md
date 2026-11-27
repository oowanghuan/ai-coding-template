# 既有会话通知修复：已验证部分与尚未完成部分

本轮修复 WP-004 运维缺口，支持 OD-07 已批准的 WP-102/103。此前后台能读到评论并持久化 pending，但没有投递消费者；缺口发生在“识别待办 → 通知既有会话”，不是等待 Owner 批准。原始故障证据仍见上一轮 [Advisor 修订记录](../advisor-7221051445/README.md)。

## 实际证据

| 层次 | 结果 | 证据 |
|---|---|---|
| 原生接口实际投递 | 固定已加载的现有会话，active `turn/steer` 接口接受；通知实际进入模型输入，并由该上下文写入 received=true | [active-context-probe.json](active-context-probe.json) |
| 桥接逻辑隔离回归 | 16 项 Fake RPC 测试通过；原 broker 38 项检查通过。没有调用真实 NativeClient 或 GitHub | [隔离结果](isolated-result.json)、两套测试源码与日志 |
| 独立发现及修正 | queue/start 超时后可能再次发起同一未知写入；实际 Fake RPC 复现两次调用，修订后永不自动重发 | [初次独立检查](pre-fix-review.json)、[复现输出](pre-fix-probe.log)、`test_unknown_start_*` |
| 已部署后台 | 15:30、15:34 UTC 两次由 launchd 实际运行，均 31 条评论、pending=0、processed=0，journal 对账完成；未重放已关闭意见 | [首轮](poll-20261127T153024269284Z.json)、[下一轮](poll-20261127T153405314707Z.json)、[部署摘要](deployment.json) |
| 真实 Advisor 自然投递 | 15:40 自然轮询读到 32 条评论、1 待办；15:40:12 投递接受，15:40:20 既有模型实际接收并核对意见 | [自然轮询](poll-20261127T154006046944Z.json)、[投递 journal](event-7222308870-delivery.json)、[模型接收回执](event-7222308870-ack.json) |
| 实际处理与公开回执 | 原会话核对限定 GO、保留开放边界、整理已完成独立证据，准备已核查 outbox；15:41 后台发布一次并回读确认 | [发布运行](poll-20261127T154145101336Z.json)、[操作 journal](event-7222308870-operation.json)、[结果评论 7222373829](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7222373829) |

[同事件关联记录](event-7222308870-chain.json)核对下一轮 15:42 读取 33 条评论、pending=0、processed=0；远端同事件 marker 仅有结果评论 7222373829 一条，未再次通知或发布。[下一轮记录](poll-20261127T154218203726Z.json)。

这些层次不能混为一谈。前两个后台零待办运行只证明部署后正常读取；原生探针由前台触发。后来真实意见 7222308870 到达，15:40 自然轮询在没有 Owner 人工提醒的情况下送达已加载、active 的既有会话。Project Lead 在该上下文确认两项修订限定 GO，不扩大为整体验收，并向台账提交一次可核对处理结果。此前的 103 项测试已先完成，不冒称由本事件自动执行。

评论含受审与实测两个 SHA，检测器保守登记 `v4-pl:7222308870:unbound`；模型接手后阅读原文，明确其受审对象为 `ed1bbd8b36df42c8a6ec0ea1f0c44ea52fee3ed6`。不猜测 SHA、不丢弃歧义事件、不据此扩大授权。用户/模型的内部会话标识在公开副本中以 SHA-256 关联，原始 journal 留在仓库外。

加载但 idle 的原生 queue/start、物理重启、离线恢复、额度恢复仍无真实端到端证据。该 active 实例的成功不能被推广为任意状态下的无人值守研发保证。15:41 发布和 15:42 去重检查均由现有 Project Lead 调用 launchctl 提前触发，仍执行原单实例后台程序；没有改变 15 分钟自然排程，也不是 Owner 人工接单。

## 实现与权限边界

部署源码是 `poll.py.txt` 和 `session_delivery.py.txt` 的原字节副本，SHA-256 与后台记录一致。机器专用绑定、原始会话历史和权限配置保留在仓库外。原 LaunchAgent、15 分钟固定时点、RunAtLoad 和 poll.lock 单实例不变；部署前在同一锁内保存原版本，替换受信通知代码，没有运行候选、写候选仓库或改变执行权限。

桥只接受一个预先绑定且已加载的 thread/cwd，走已有本地 daemon Unix socket，方法白名单没有 thread/start、thread/resume、模型或权限设置。active 时使用带 expectedTurnId 的 steer；idle 时仅可启动本事件的明确 queuedSubmissionId，并要求队列只有这一项，避免假定默认排序或抢先执行用户队列。unloaded 时保留待办，不能创建新会话冒充接管。

事件按评论 ID、受审 SHA 和正文指纹持久化。通知只含固定说明、公开评论链接和指纹，不转抄外部评论中的指令。发送前写 intent；未知结果只核对队列/历史，不因未找到结果而盲重发。尤其 start_intent 即使仍能看到队列项，也不再次启动。

原生 accepted/history_confirmed 明确显示 awaiting_model_ack；接收回执是独立文件，须核对事件、client ID、正文指纹和既有上下文。接收不代表处理完成；公开回复仍经前台核查后的 outbox、精确远端 SHA 和评论回读确认。对已关闭事件不再通知或运行。

## 后续验证

后续真实、已授权且未处理的 Advisor 事件同样关联评论 ID/受审 SHA、poll run、通知 intent/原生 receipt、模型 ack、首个实际处理结果、公开回复与下一轮零重复记录。若停在任意一层，保留准确状态，不要求 Owner 再输入“继续”，也不擅自开启新模型会话。当前待补的是 idle/恢复等不同运行条件，而非重放已经处理的 7222308870。

电脑休眠、离线或既有会话卸载时不能保证实时处理；恢复运行后读完整分页与持久化 journal 补读。原生接口来自本机已安装 daemon 的生成 schema，属于实验接口；版本变化时须重新探测和验证，不能把这台机器的已验证配置称为通用 Codex Adapter。

公开源码仅供审查本项目受信运维桥，不纳入项目安装器或候选执行目录。`source-index.json` 记录原始来源指纹；`artifact-index.json` 对公开副本逐文件校验。运行与测试数字只覆盖各自对象，不计入 当前 WP-102/103 的 103 项回归总数。
