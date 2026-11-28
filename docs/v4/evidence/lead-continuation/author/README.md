# Project Lead 续做唤醒候选：作者证据

当前外部轮询主要由新 Advisor/Owner 事件驱动；没有新评论时，不会仅因已有 ready 工作而唤醒处理。此处保留最小候选原型及 Fake 测试证据，供与既有协作实践共同评审。它尚未部署，也未被定为 V4 正式调度架构。

候选仅复用已有 loaded 会话与原轮询单锁。任务仍来自公开 `V4_WORK_PACKAGES.md` 的有限机器可读 ready 片段；本地仅保存投递、ACK、公开进度观察和保护配置。没有新模型会话、权限变更、费用、远端写入或生产轮询修改。

## 实测

- [初版运行](result-01.json)：19 项通过，0 跳过，输入不变。
- [最终运行](result-04.json)及[原日志脱敏副本](stderr-04.log)：41 项通过，0 跳过，exit 0，输入不变。包含 22 项续做测试、3 项原轮询单锁/GET 边界测试、16 项既有 Advisor 桥 Fake RPC 回归；数字不与早期运行相加。
- 中间运行 02（38 项）与 03（40 项）原件仍保存在仓库外，未重复复制。

所有候选导入/执行均在 A01 外层沙盒；[命令与环境](result-04.json)、[调度脚本文本](harness/run.py.txt)、[沙盒配置](harness/profile.sb)可核。证据级别是 `synthetic_fixture`，真实 Native IPC 调用与 GitHub 请求均为 0，`provider_live=false`。这不证明真实 launchd、真实空闲会话唤醒、机器重启或持续多轮工作的集成已通过。

## 可评审机制

详细说明及默认暂停示例见[候选说明](candidate/README.md)与[保护配置示例](candidate/config.example.json)。实现文本为 [continuation.py](candidate/continuation.py.txt)，原轮询接线候选为 [poll.py](candidate/poll.py.txt)。[session_delivery.py](candidate/session_delivery.py.txt)保持原桥字节；续做使用独立事件，不调用其 active steer 路径。

关键保护：未 ACK 或未知投递不能创建下一 activation；ACK 不等于完成。同一任务和公开进度跨批次最多两次唤醒后 stalled，远端改批次名不能重置本地总上限。Owner 评论集合变化要求 Project Lead 对账并更新已读缓存，不是让 Owner 每步重新留言或批准。新增重复 JSON 键拒绝，避免人工看到 paused 而机器取后面的 running。

Native queue 接口没有原子 idle 前置条件。候选在写前核对 idle，若随后观察到 active，只保留队列、不 steer/start；不能宣称严格原子的 active 永不入队。已确认 add 但尚未尝试 start 的队列项，可在后续 idle 轮首次启动；未知 add/start 一律只读对账。公共文档进度是 Lead 的记录，不自动升级为独立工程验收证据。

[public-manifest.json](public-manifest.json)逐文件列出原始与公开副本 SHA256；公开副本替换本机路径，不能冒充原始可信 receipt。测试内 thread ID/cwd 均为合成夹具；没有复制生产 session binding、真实 thread ID、原机 socket 配置、登录输出或私有项目资料。此处由实现作者验证，独立审核结论另列，不能自签验收。
