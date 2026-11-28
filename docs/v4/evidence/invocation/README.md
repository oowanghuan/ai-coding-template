# 通用调用入口及本机认证对照

后续 [跨 Adapter 整改](../cross-adapter-launch/README.md) 已复现本历史版本的防重范围
缺口：以下“换键不能重跑”仅在单一日志域内成立，旧三适配器用例也不证明跨绑定
防重。此处保留历史运行，不将其71项通过解释为跨供应商安全接管通过。

最终实现：`d815cf4a542316d14524d3cbc2891e9fb8b2b0a7`。
Owner 直接要求继续推进后，在原 OD-09 / WP-301 范围实施；不等待 B1 复核才开工，
没有新增或充值 continuation 批次，没有启动其他模型会话。

## 实际交付

`AdapterRegistry` 增加显式绑定 executor 的 start/status/stop/result。新
`ProcessExecutor` 使用固定 argv/cwd/显式环境及输入指纹，启动前两次调用受信
授权检查器，先保存启动意图再启动实际进程。提案数据不能提供程序或环境；
同请求重放返回原 invocation，换请求ID也不能重跑同一执行权/工作目录。

监督线程实际读取输出、限制总大小和时限、观察退出码；停止请求与实际退出分开。
控制器丢失 owned handle 时，未结束记录显示 outcome_unknown，不凭磁盘PID杀
进程或重新启动。结果始终 untrusted_stdout / engineering_accepted=false；
writer_stop_confirmed=false 保留“主进程退出不等于全部写者停止”的边界。
新的外部调用路径拒绝 direct-local-only 命名空间，保持旧未启动恢复证明的前提。

这是一项可执行组件，尚未部署为真实供应商服务。默认供应商入口不会因添加类而
自动获得启动权限。运行绑定、Store 实时授权接线、持续控制器、健康检查和真实
Claude/Codex任务仍待完成，见 [调用说明](../../../../framework/adapters/README.md)。

## 实测及失败记录

| 运行 | 结果 | 说明 |
|---|---|---|
| [initial](initial/stderr.log) | 65方法：52通过、13 error，退出码1 | 漏带三份规则入口fixture；新校验把系统Python的合法硬链接当成非法文件，12个调用测试未进入执行 |
| [intermediate](intermediate/stderr.log) | 65全过、0 fail/error/skip | 补齐只读fixture；系统程序允许合法硬链接，仍核对非符号链接及精确哈希，日志单链接规则不变 |
| [pre-boundary-refinement](pre-boundary-refinement/stderr.log) | 68全过、0 fail/error/skip | 增加并发同键一次启动、子进程关闭输出后仍可停止、输入pin变化拒绝 |
| [final](final/stderr.log) | **71全过、0 fail/error/skip**，退出码0 | 再验证换请求ID/新token不能复用原工作目录，以及专用恢复命名空间拒绝 |

71项包括18项调用测试和53项原适配器/解析/规则入口回归；不累加中间轮次。
实际启动固定 Python 进程，验证stdin/stdout/stderr、错误退出、超时、输出上限、
停止、并发重放、恢复未知状态及篡改拒绝。三个不同工具/模型供应商选择通过同一
接口执行，无新增核心供应商分支。这是合成选择与真实固定进程证据，不是三家
供应商真实调用，也不是第三Adapter完整资源池验收。

四次均各9项A01隔离检查通过，源及冻结文件不变，宿主无候选导入、无模型调用。
只读冻结输入清单和测试选择器随范围更新，沙盒/凭证移除/网络禁用均未放宽。
最终32项输入逐blob绑定上述最终实现；早期原型不同的源码另存文本快照，
见 [版本绑定](SOURCE-BINDING.json)、[汇总](SUMMARY.json) 和
[原始/公开双哈希](FILE-MANIFEST.json)。原始失败完整保留，原件仓外持久保存；
替换机器路径的公开副本仅作复核材料，不冒充可直接重放的可信执行包。
本批为作者运行，独立复核未完成。

## Claude 历史认证失败已缩小到可复现的环境条件

[只读认证观察](original-auth-status.json) 显示两家已安装CLI在现有合法环境中
都已登录、退出码0。对Claude 2.1.332，同一二进制和
`--safe-mode --restricted --setting-sources '' auth status`：

- 原有环境：logged_in=true。
- 仅HOME/PATH/LANG/LC_ALL：logged_in=false，退出码1。
- 最小环境只加回原有USER：logged_in=true，退出码0。
- 单独加回LOGNAME、SHELL、原PATH或所测OS会话变量组：仍false。

这是本机/当前版本的实测差分，不推断供应商内部认证实现。历史清理环境遗漏USER
导致的失败可复现，不能再当成账号未登录或CLI本身不可用。没有复制凭证、保存
身份变量的值、修改登录/配置、关闭隔离或发起模型调用。原始认证输出保持仓外。
后续受信执行环境应保留必要的本机身份上下文，同时独立核查工具、凭证和写入
边界；本次认证状态成功不能代替真实任务执行、额度恢复或安全部署验收。

原B1忙碌准入仍等待其独立复核/非作者执行，不被本轮结果关闭。真实供应商、
完整Lite Alpha、跨机与发布仍未验收，main未修改。
