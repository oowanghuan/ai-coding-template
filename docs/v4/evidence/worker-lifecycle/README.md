# Worker 生命周期第一可运行增量

产品代码提交：`e4a7d974abb481e357106f64dacac2fe2e9d7440`。
补充完成后重复恢复测试提交：`f5404183307326c27c8a994fada277e0b4312b22`，实现代码未变。
这是 OD-09 范围内的 N 供应商协议、确定性生命周期、文件检查点和合成进程集成，
**不是两家真实 Coding Agent 已接入，更不是完整 Alpha 通过**。
Owner 已明确批准 301/302/303 和优先级，见 [OD-09](../../OWNER_DECISIONS.md)。

## 已实际运行

- [十组实际回归](regression/ASSESSMENT.json)：346 项中 343 pass、3 个原 direct skip，
  0 failure/error，各组的 5 项隔离探针通过。原始宽输入表为 false：运行时新增
  `examples/alpha/README.md`；原已登记的 76 项输入全部不变并逐字节匹配产品提交。
  [原结果](regression/result.json) 保留该例外，不改写为全部冻结。
- [完成后重复恢复补测](completed-recovery/result.json)：在真实 demo 完成后重新读取
  持久状态，对同一恢复操作重放两次，随后以新操作 ID 提交已处理 probe；前两次只返回
  原 receipt，后一次拒绝。状态、所有 Workspace 文件及操作流水不变，没有新增进程。
  这是 Advisor 7235366840 所提的同机反例，单项实跑通过，未重跑整套 346 项。
  本地固定写者动作不增加，真实外部 API 调用为 0，不宣称跨服务 exactly-once。
- [非作者独立验证](independent/README.md)：53 项 Adapter、26 项 Recovery、29 项
  Lifecycle/Handoff；独立实际进程演示及经过逐字节预审的单命令 helper。
  最终 29 项的宽输入表有一项变化：新建但该测试不使用的 helper；原结果仍保留 false，
  受测 framework/schema/fixture/test 闭包前后不变，另有明确的范围分析。
- [开发期原始记录公开副本](author/README.md)：包括首轮夹具初始化错误、
  `baseline_sha` 解包错误与修订；重复运行、失败及源码变化记录不改成成功。
- 独立 helper 在全新 T/C 冻结源码和现有依赖，8 项隔离探针先通过，然后实际运行
  两个固定合成进程。A 被注入额度限制，执行权失效；确认实际退出及进程组消失，
  保存 dirty/untracked，B 用更高 token 在新 Worktree 接管。A 恢复只回池，
  旧 token 和第二次提交被拒；两个任务各形成一次逻辑交付，PMO/model 调用为 0。

单命令入口及边界见 [可运行说明](../../../../examples/alpha/README.md)。
启动器 SHA256：`ea4b7505c3a0665278a3278b6661492c5930e943aefc2c5d6e2943530eefc337`。
它只运行固定合成例子、不安装依赖、不配置后台服务、不调用模型。不要用环境变量
模拟沙盒或把候选仓库代码直接放到宿主运行。

## 真实供应商：明确待验证

| 检查 | 实际结论 | 下一步 / 责任 |
|---|---|---|
| 官方 CLI 元数据 | Codex 0.169.0、Claude Code 2.1.332；固定帮助/版本探测成功 | 只证明程序可运行，不证明认证/额度/模型任务 |
| Claude 认证 | 在本次固定受限参数/环境下，官方 status 报未登录，远端 managed 设置无法获取 | Owner 通过官方 CLI 登录已有订阅后通知；Lead 重检，不接收或复制凭证，不新增 API 费用 |
| Codex 认证 | 官方 status 识别 ChatGPT 认证 | 不证明剩余额度；Lead 继续准确执行边界验证 |
| Codex 原生权限 | 命名最小权限可限制测试文件/写入/网络；但合成进程环境探针仍可读取 marker | 尚未满足完整 A01；不能发布为可用真实 Worker |
| 组合强化策略 | 增加拒绝其他进程信息的外层后，原生内层 `sandbox_apply` 退出 71，探针未运行 | 不关闭保护兜底；Lead/Reviewer 继续检查可受控的工具面或单一有效执行边界 |

账户诊断原件仅保留仓库外，公开的是安全摘要和原件指纹，见 independent。
真实模型调用、真实额度受限/恢复、无人值守真实 probe、供应商原生 Session 恢复
均未验收；没有通过切号、共享凭证、故意耗尽额度或额外付费获取证据。

第三个合成 Adapter 已经走统一注册/分类与核心匹配、认领、暂停、恢复、checkpoint、
交付链；其进程执行仍由固定演示 supervisor 提供。这个结果证明当前核心无需按供应商名
分支，不能扩成所有 Adapter 已有通用 native start/status/stop 实现。

## 未完成边界

当前保持单 Host 合作控制器信任模型；角色字符串/可信观察不是跨机认证。
`cycle` 能独立生成认领与持久 probe intent，但尚未接实际供应商探测执行器或安装守护服务。
Prepared 但从未启动的任务保全且禁止无快照接管，完整自动 no-writer 对账路径仍未实现；
正向证据针对运行过且拥有实际进程句柄的场景。Dedicated/Elastic/Restricted 尚为
元数据，不声称时间窗口和全部限制已执行。真实质量 Gate/签认与这条用户路径的最终
连接、已有项目正常用户首任务和完整 Lite UX 仍待完成。

所有原/public 指纹分列；脱敏副本不能冒充原始受保护收据。历史测试数不累加成一次
最终回归，最终提交绑定由 [COMMIT-BINDING.json](COMMIT-BINDING.json) 给出。
