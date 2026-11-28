# 首份交付接入真实证据 Gate

代码提交：`7ca3622908937339e6e064fd8e6e49fff8c914a5`。
Advisor [7238038580](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7238038580)
已对受审版本 `d151b5367ed3a1ee65a2a046ad303688ab4dc97c` 给出限定 GO：仅覆盖
固定文本交付的取证与质量检查。评审为只读查证，不计为新增测试或整个 WP-303 验收。
入口：`scripts/run_worker_demo.py --verify-first-delivery`，操作方式见
[Alpha 说明](../../../../examples/alpha/README.md)。本批复用既有 collector/Gate，
未修改调度、恢复、质量核心或原合成演示。它验证首份文本交付，不是实际供应商
任务、代码功能验收或完整 Lite Alpha。

本次由 [自然定时续做](../lead-continuation/live/README.md) 接手 WP-303。
实际文件、交付记录字节和摘要先交叉核对；独立固定预期内容再由真实 Python
checker 执行验证。原开发基线与新取证快照提交分开，后者包含实际成果、固定
checker 和来源记录。摘要自洽不等于内容正确。取证不会修改主任务权威状态。

| 验证 | 已观察结果 | 证据 |
|---|---|---|
| 非作者边界测试 | 最终 e1dc 启动器版本 14 pass、0 skip；九项隔离探针通过，原/冻结输入不变 | [运行记录](independent/unit/result.json)、[逐项结果](independent/unit/stderr.log) |
| 作者真实进程闭环 | 演示成功后真实 collector 执行 1 项、1 pass/0 fail/0 skip；Gate passed；权威状态不变 | [启动器结果](author/result.json)、[collector 原始结果](author/quality/evidence.json)、[Gate 结果](author/quality/gate.stdout.log) |
| 分层隔离 | 演示外层八项、checker 五项、Gate 七项探针通过；无宿主候选模块导入 | [外层输出](author/stdout.log)、[checker 日志](author/quality/logs/document-bytes.stderr)、[Gate 探针](author/quality/gate.stderr.log) |
| 准确版本 | 作者 29 个冻结项目输入逐 Git blob 核对；启动器和测试精确哈希单列 | [源码绑定](source-binding.json)、[启动记录](author/launch/result.json) |
| 独立真实正例 | 新实验目录实跑，collector 内容检查通过、Gate exit 0；主状态不变 | [独立报告](independent/REPORT.json)、[运行汇总](independent/integration/result.json)、[Gate](independent/positive/quality/gate.stdout.log) |
| 独立错误但自洽内容 | 新实验中更改真实文件并同步交付摘要，固定预期保持原值；collector 完成但内容检查失败，Gate exit 1 | [受控变更](independent/integration/negative-mutation.json)、[失败原因](independent/negative/quality/gate.stdout.log) |
| 同一取证意图重放 | 第二次 collector exit 2，明确已有 intent；原证据、scratch 文件集合及原 case PID 不变，未新增测试执行 | [重放记录](independent/integration/collector-replay.result.json)、[原始错误](independent/integration/collector-replay.stderr.log)、[断言汇总](independent/integration/result.json) |
| 伪造通过报告 | 候选中自报 passed 且摘要自洽，受保护注册无该运行；Gate exit 2，精确原因为 `trust:unregistered-run` | [Gate 输出](independent/integration/fake-receipt.stdout.log) |

作者新取证提交为 `bfc6540219eb4351460d444784797965bf744ca2`，不是 Worker
提交的代码版本，也不是原开发基线。真实命令、进程、退出码、plan/trust pin、
Git 对象、内容摘要、stdout/stderr 和来源绑定均保留；真实模型调用为零，
`provider_live=false`、`engineering_accepted=false`。

独立执行者没有实现启动器，另建现场设计并执行上述四个场景；边界 Reviewer
再只读核对记录，不重复计一次实跑。独立正例 29 个原项目输入、负例默认演示的
原 28 个输入及另加固定 CLI 均绑定同一代码提交。负例保留原 `inputs.json`，
新增项记录于 [negative-frozen-inputs.json](independent/negative/negative-frozen-inputs.json)，
并 [单列绑定](independent/negative/added-cli-binding.json)。错误内容由受审协调器
在全新负例现场受控写入，原字节另存；其后的 `authority_unchanged=true` 指取证
阶段没有再改这些字节，不是声称负例从未修改原始演示成果。

范围内结论为“合成文本成果进入真实 Gate 的正负路径已验证”。四个场景符合预期
不等于四份成果都 passed，更不意味着工作包最终验收、真实供应商或跨服务
exactly-once 已成立。普通不带选项的演示也在独立负例准备中实际通过。

测试准备中拒绝过一个写范围过宽的旧外壳，未执行该版本。改为新 E/T/C 的
收紧外壳后才进行测试，详见 [预审记录](independent/preflight-review-rejection.json)。
早期 ddfe 版本也有 14 项通过，原件保留仓库外，不与最终版本累加。
日志中的系统 Python/xcrun 缓存写入拒绝警告原样保留，没有将其删除或改写为成功。

原始运行材料已保全于仓库外持久目录。公开副本仅替换机器路径，并保留
[原始/公开双哈希](FILE-MANIFEST.json)。它们是复核材料，不能当作可直接执行的
可信证据包；路径替换后的 plan 哈希当然不同于真实运行的原始 pin。
实际供应商、自然额度恢复、跨机、重启恢复和独立工程验收仍待验证。
