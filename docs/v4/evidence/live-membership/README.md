# 已启用资源池的动态 Worker 登记

实现提交：`6c78c133fd483c210317e20d5d400ff6521eeeaf`。
沿用 OD-09 的 WP-302 / B1，第四次自然续做投递触发；没有新建或恢复其他模型会话。

原先 `register-worker` 在生命周期启用后直接拒绝。现在可在同一个 Store 锁和
原子提交中加入新 Worker、Host、Provider、Session 及 runtime 记录。已有身份不可
迁移；正确的同 operation/intent 可重放，不重置已认领任务。不同意图、旧 revision、
引用不一致或缺少 runtime 配置均不能留下部分登记。

已有有效 Assignment、token、工作区和其他成员保持不变。共享额度组的限制、
generation、pending probe、恢复时间及重试数不被新成员重置；新成员额度观察与
现有不限额组冲突时拒绝登记，先通过原 worker-event 路径核实并应用组限制。
未知认证、授权、预算或受限额度不能接单；登记新 Host 不授予该 Host 任务执行权。
符合条件的新成员可通过现有能力/权限/范围/并发规则认领另一任务。

接口说明：[本地控制器](../../../../framework/local/README.md)。认证布尔值由受信
本机控制器提供，不接受远端申请者自报作为可信认证。本次没有认证发现、真实 CLI
启动、后台 Worker 安装、跨机接入或身份/额度组自动迁移。

## 实测记录

新增 [13 个测试](../../../../tests/lifecycle/test_worker_membership.py) 在独立临时 Git
及真实状态文件上运行：13 pass、0 fail/error/skip，退出码 0，9 项隔离检查全部通过。
见 [逐项日志](targeted/stderr.log)、[计数和隔离检查](targeted/stdout.log)、
[实际启动参数](targeted/launch.json)、[运行结果](targeted/result.json)。

覆盖活跃任务保全及新任务认领、重放与冲突、已有共享额度/未决探测保全、缺认证和
授权、身份引用与不可变对象、非法 resource、未知额度、Host 权限、能力/预算/离线、
相同 revision 的真实线程并发竞争，以及提交前故障无写入/提交后丢响应的安全重放。
认证和额度输入是合成观察，不是供应商认证或真实额度事件。

另一次使用未改动的既有受审外壳运行完整所选回归：**108 pass、0 fail/error/skip，
退出码 0**，9 项隔离检查通过。覆盖生命周期、停止/未启动恢复、动态登记、外部
启动客户端与 Driver；见 [完整逐项日志](regression/stderr.log)、
[实际结果](regression/result.json)、[汇总](SUMMARY.json)。这 108 项已包含上述
13 项，不合计成 121 个不同用例。两次冻结输入完全相同，均绑定同一实现提交。
本轮回归成功不覆盖或抹去上一恢复批次保留的测试 hook 失败记录。

本轮由实现作者运行，**独立复核与非作者复跑待完成**。没有把“隔离运行”写成
“独立评审”。使用此前受审外壳，仅将测试 discovery 选择器改为新测试；沙盒、
冻结输入、凭证清空、网络禁用、超时及日志路径不变，差异及指纹见
[selector-review.json](selector-review.json)。候选框架只在隔离子进程导入，
宿主外壳仅使用标准库；本次没有供应商调用、凭证复制或生产 Driver 更新。

测试启动时 HEAD 仍为前一计划提交，工作树已包含新实现。24 项冻结源码/Schema/
fixture 输入逐一与随后形成的实现提交 blob 比对一致，见
[SOURCE-BINDING.json](SOURCE-BINDING.json)。源文件、冻结副本及外壳控制文件
在运行后均无变化；不以启动前旧 SHA 冒充实际测试对象。

原始日志与启动材料在仓库外持久保存。公开副本只替换实际机器路径，原始/公开
双哈希见 [FILE-MANIFEST.json](FILE-MANIFEST.json)。副本用于复核，不能作为可直接
重放的原始可信执行包。历史外壳的文件名/scope 含 prepared-recovery，不改变本轮
实际测试选择器与日志所证明的范围；本说明明确区分当前登记验证和旧恢复回归。
系统 Python 缓存写入被拒绝的原警告保留，没有扩大权限消除警告。

本切片尚待独立审查，不标记工程验收完成。真实供应商执行、自然额度恢复、跨机、
正常用户免手改状态的完整入口及整个 Lite Alpha 仍未验收。
