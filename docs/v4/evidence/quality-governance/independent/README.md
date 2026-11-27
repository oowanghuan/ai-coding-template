# WP-201 / WP-203 独立执行与边界复核

受测代码提交：`580cc0a8ce40fe9d4d235f94d7ab1e7aba2ddafc`。固定 collector SHA256：`f4ad7874c7dc9415f4dc0d1d26f2d4d095b42ef7580b786152f0886452d9ab6f`。独立运行记录中的产品输入已逐一匹配该提交的 Git blob，见 [commit 绑定](commit-binding.json)。

本目录的 reviewer 没有实现产品代码。复跑使用全新 T/C 和实际进程，未把作者产物算作独立执行。基础场景复用了已审查的作者测试设计；SIGINT 实验、假独立身份和候选域伪来源反例由 reviewer 另行编写，并由 Project Lead 审查固定协调器哈希后执行。

## 实际结果

| 范围 | 结果与边界 | 证据 |
|---|---|---|
| Collector / Gate | 11 场景全部得到预期结果；包括实际成功、非零失败、超时、关闭输出后继续运行、输出超限、必需 skip、零检查、文档检查、拒绝 fork、边界检查、无 collector 的假报告 | [汇总](quality/run/summary.json) |
| 重放 / 错 pin | 原操作重放 exit 2，T 内字节不变；错误 trust pin 返回 unverifiable | [重放](quality/run/replay.json)、[错 pin](quality/run/success-gate-wrong-pin.json) |
| SIGINT | 对本次 owned collector 发 SIGINT；首 case 已观察 exit -15，receipt 为 unknown；后续 case 无 scratch/policy/log，intent 保留，Gate unverifiable；重放未改变 T 字节 | [实际记录](interrupt/run/result.json) |
| 治理联合链 | 19 条真实 CLI 均符合预期；使用本次新 collector 产生的真实 Gate 结果 | [汇总](governance/run/summary.json) |
| 假独立身份 | role 声称 reviewer，但 principal/context/group 与作者相同：rejected | [拒绝记录](governance/run/06-false-independent-role.json) |
| 候选域伪来源 | 复制 review 记录到 C，并配套提供正确内容 hash：仍 unverifiable | [拒绝记录](governance/run/07-candidate-forged-review-source.json) |
| 契约变更 | 改变契约、再恢复原契约，旧签认均不能自动复活；重新实际取证和 R2/S2 后才 effective | [变更拒绝](governance/run/11-contract-changed.json)、[恢复仍拒绝](governance/run/12-contract-restored-old-signoff.json)、[新证据复签](governance/run/14-fresh-review-after-restore.json) |

负向场景的断言通过，不等于对应 Gate 通过。例如 selfreport/timeout/flood 的正确结果是 failed，缺失可信执行的正确结果是 unverifiable。治理记录中的身份均为合成 fixture；`effective` 表示规则计算结果，不是实际人类或项目验收签字。

## 独立审核发现与实际修正

Collector 静态审核覆盖了固定 argv/环境、Git blob→tree→commit 绑定、有限输入输出、独占 intent、已观察退出、只向本次持有的进程发信号，以及 unknown 不重放。发现并修正了中断后继续启动下一 case 的路径；实际 SIGINT 反例另外验证了修正。

候选 Python 可能派生后代，因此不能仅凭父进程退出声称已收束。固定系统探针证实：保留 `process-exec`、拒绝 `process-fork` 后，Python/stdio 可用，fork、subprocess 和 posix_spawn 被拒。`start_new_session=True` 保证测试进程为 session leader；其 setsid/setpgid 失败是该内核约束，不冒称额外沙盒权限检查。见 [可行性记录](probes/fork-feasibility/result.json)。

只移除 `sysctl-read` 放行仍不足以阻止读取其他进程环境：针对 reviewer 自己创建、仅含公开 marker 的临时进程，实际读取成功。显式拒绝 sysctl-read 仍失败；全局拒绝 process-info 导致系统 Python exit -5，未被算作可用方案。最终明确拒绝 `process-info* (target others)`，同时保留 Python 正常运行，才实测拒绝该合成进程读取。全过程没有读取真实凭证或无关 PID。

- [无 sysctl 放行仍可读取](probes/procargs-no-sysctl-grant/result.json)
- [显式 sysctl 拒绝仍可读取](probes/procargs-explicit-sysctl-deny/result.json)
- [全局 process-info 拒绝导致启动失败](probes/procargs-deny-all-process-info/result.json)
- [拒绝其他进程信息后通过](probes/procargs-deny-others/result.json)

第一条探针没有设置独立 session，因此其中 setsid 观察不用于 collector 的进程收束结论。后续探针和实际 collector 均明确使用独立 session。

安全读取采用逐段 O_NOFOLLOW 目录 FD。本机 Darwin 的 O_SEARCH 可固定祖先而不要求目录列表权限：父目录不可 list、外部 leaf 不可读、祖先换链被拒；已固定父 FD 后换链仍读取原文件。见 [实际 O_SEARCH 反例](probes/search-fd/observations.json)。这只是本机验证，不是跨操作系统可移植性证明。

## 最终生成策略的实测

固定 collector 仅在 hardened A01 内 import 以生成策略；其后宿主运行的是已审查的固定系统 Python 探针。实际生成策略下，T plan/receipt/log 的读写、subject 写入、外部/sibling/checkout 读写、网络、fork/posix_spawn/subprocess，以及合成宿主进程环境读取均被拒绝。subject 读取、自身 scratch 写入与 stdio 正常，原始受保护字节未变。见 [完整命令与结果](probes/actual-collector-policy/probe-result.json)。

通过该审核后才执行固定 collector 的宿主副本。测试入口运行于其独立沙盒；Gate 和 governance CLI 始终在外层 A01 中运行。外层使用显式的其他进程信息拒绝规则，未为兼容旧代码增加 sysctl 权限。

## 如何核对文件

[导出清单](export-manifest.json) 对每份公开副本分别列出原件 `original_sha256` 和脱敏后 `public_sha256`。JSON 中原有的 plan/receipt/log 哈希仍指向原始字节；不能直接用脱敏文件计算的哈希替代。路径使用 `<REPOSITORY>`、`<QUALITY_EXPERIMENT>` 等占位符；`.py.txt`、`.sb.txt` 是审核副本，还原路径后才能复现。只归档实际保留的源文件，没有从新版代码逆向拼造早期快照。

`quality/trusted/`、`interrupt/trusted/`、`governance/trusted/` 保留配置、原始日志的公开副本、收据、策略、来源记录和账本；各 `run/` 保留真实命令、退出码和验证结果。`untrusted-inputs/` 中的假报告仅用于反例，绝非权威证据。二进制系统启动缓存不发布。

该批仅验证有限的本机 Python stdio 检查及本地治理规则，不是通用单元测试/插件引擎、不抵御恶意机器所有者、不证明测试设计完备，也不代表供应商、云端、合入、部署或业务验收。旧 direct 后端未测项仍单独保留。
