# Store 实时执行权接线

实现提交：`64704dca23d73a73c433d34d8723d4b6a661fc85`。
Owner 在盒盖后要求继续推进，本轮从已保存检查点续做 OD-09 / WP-301；没有重置
自动唤起预算、创建模型会话、修改权限或部署真实供应商执行器。

[Advisor 7242414495](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7242414495)
已对受审 `4f29feed191a964ce65919db52eac7148c3f0693` 给出单机启动前检查及意图落盘
的源码限定GO。最后授权检查返回至Popen之间、以及运行中撤权的及时停止尚未验证。
此状态更新不重跑或追加测试，不把源码GO当作真实执行或阶段放行。

## 交付与实测

`framework/adapters/store_binding.py` 提供 StoreBinding：将固定执行选择和准备好的
工作区绑定到现有权威 Store。实际启动前，锁内核对执行者、epoch/token、租约、
当前工作包/基线、规范与授权指纹、预算/暂停、依赖一致性、Worker认证/健康/Host、
工具/模型供应商/凭证引用/共享额度，以及真实Git worktree和基线。

同一Store原子写入 `provider-run-begin` 操作及workspace launching意图，再预留
共同启动域，之后才可能创建进程。任何步骤结果未知都不回滚为“可以再启动”。
替代控制器即使换输出目录、操作ID或错误配置成新预留域，仍被Store旧启动意图阻止。
共享预留机制及其原受审版本保持独立复核范围。

| 运行 | 结果 | 证据 |
|---|---|---|
| 初轮 | 87方法全过，0 fail/error/skip，退出码0 | [完整日志](initial/stderr.log) |
| 最终 | **88方法全过**：11项新Store接线 + 77项原适配器/调用回归；0 fail/error/skip，退出码0 | [完整日志](final/stderr.log)、[实际观察](final/stdout.log) |

最终增加了Store提交后回执丢失用例，强化了启动时序观察和错误新预留域的反例。
包装的Popen仍执行真实固定Python进程；调用实际Popen前读取Store，观察到
workspace=launching、provider-run-begin操作数=1、writer_stop_confirmed=false。
进程实际退出0后，任务仍in_progress，workspace仍未完成，release被拒绝。

其他覆盖：错误token/epoch/工作区/工作包/基线/选择、租约和心跳过期、Owner暂停、
预算未知、授权撤销、规范变更、Host离线、认证失效、未恢复检查点、错误cwd；
启动预留后最后一次检查前额度变化不启动；Store提交前失败无部分状态；提交后
回执丢失或共同预留不可用均保留未明状态。共享Q1受限阻止原Worker，独立Q2的
任务仍由真实固定进程执行，不依赖PMO模型做状态转移。

两轮各9项A01隔离检查通过，源及冻结输入不变，宿主无候选导入。固定外壳SHA256：
`bca8949ff04ba3639bae10889ab5607995fdd8bffb83c93f5259a56b58c69370`。
仅增加冻结只读fixture及其导入路径、运行标签；执行保护、网络/凭证限制未放宽。

[SOURCE-BINDING.json](SOURCE-BINDING.json) 绑定最终35项输入的提交blob；初轮两份
不同源码作为文本快照保留，不冒充最终版本。[SUMMARY.json](SUMMARY.json) 和
[FILE-MANIFEST.json](FILE-MANIFEST.json) 保存运行摘要及16份原始/公开双哈希。
原件仓外持久保存，公开副本仅替换本机路径，不是可直接运行的可信部署包。

## 适用范围及剩余工作

全部是作者运行的真实临时Git/Store和固定进程测试，认证/额度观察为合成输入，
独立源码复核已获上述限定GO，非作者执行待补；不是两家供应商真实任务或真实额度恢复。

本组件仅完成启动前接线。它不持续监控已运行进程，不把主进程退出当作全部写者
已停止，不自动提交/验收/释放任务；进程启动后的撤权仍需受信监督器停止、检查点
和恢复闭环。真实CLI工厂及权限边界、终态对账、持续服务、正常用户入口、自然
额度恢复和完整Lite Alpha仍待验，不能因88项通过就放行实际部署。

[后台观察](poll-observations.json) 保留15:55和16:10 UTC两轮真实定时读取：各70条
评论、pending=0、成功结束；旧4/4续做预算耗尽单独记载，未自动充值。此记录证明
这些轮询实际发生，不证明盒盖睡眠期间运行、唤醒恢复或新一轮无人值守开发验收。
