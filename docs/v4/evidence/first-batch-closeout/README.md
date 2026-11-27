# 首批独立复核收口与受审对象识别修正

[Advisor 7217342565](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7217342565) 对 `673d6baa13283180b342f446bcadc17ad66efaf9` 给出限定 GO，关闭 WP-001/101 上轮两项整改。`review-record.json` 保存范围化结论。Advisor 独立核对代码、断言和作者原始输出，未执行候选；57 项组件测试仍是作者实测。此处不把 review_passed 扩成 main 合入、完整工程验收、Alpha 或下一批授权。

受审代码和 Draft PR #5 冻结不变；本目录及下一批计划位于单独的 `v4/next-batch-plan` 分支。没有为文档收口重复运行已通过且未变化的产品测试。

## 一条评审被拆成两个任务的实际问题

`before-run.json` 是 11:55 UTC 的自然运行：读到 22 条评论、pending=2。两项来自同一个 Advisor 评论：准确受审 SHA `673d6baa…` 和比较链接内的测试代码 SHA `ea89d0c…`。原匹配器遍历正文所有 SHA，又因请审同时列出测试与受审版本而把两者都当成处理对象。

修复优先读取明确的受审 SHA，来源/比较 URL 不产生额外目标。没有明确目标且存在多个 SHA，或标签相互冲突时，保留一个 unbound 待核查项；没有 SHA 的有引用意见也不静默丢弃。仍须来自已识别账号并引用已有请审；结果不自动授予执行权。

`poll.py.txt` 为实际部署源码，`test_poll.py.txt` 为测试源码。`broker-tests.json`：**38 项通过，0 失败**，包含原有身份/端点/未知结果/去重边界，以及受审与测试 SHA 区分、比较 URL、歧义/缺失目标、真实 GO 评论重放、单次收口后无第二项残留。

先以本机保存的完整 22 条公开评论做隔离重放，再以 `real-input.json` 中两条相关公开评论复跑并保留对应指纹。公开夹具仅包含必要的评论 ID、作者登录名和正文；不发布其他本机运行输入。测试无网络，沿用 [A01 隔离策略](../first-batch/README.md)。复跑时将两个 `.py.txt` 源文件恢复为同目录 `poll.py` 与 `test_restricted.py`，并带上 `real-input.json`；候选只能在无发布凭证的隔离环境运行。

`after-selection-fix.json` 是修复后的真实后台读取：仍读 22 条，pending 从 2 变成 1，准确指向受审版本。随后通过受限后台发送 [GO 收口回执 7218049755](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7218049755)，没有新请复核请求。发布与下一次运行记录见本目录 `closeout-run.json`、`dedup-run.json`，均为同一 launchd 任务的 kickstart 实跑，不混称自然调度。

此修正只影响已有本机接收/回执，不启动 WP-402 或无人值守模型。单实例、重启后补读、未知发布结果先对账、只允许 #3 文字写入的边界保持；机器休眠/离线时不能保证运行。所有新增公开记录的字节指纹见 `sha256.json`。
