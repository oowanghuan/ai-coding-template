# WP-201 / WP-203 本地工程验证

产品提交：`580cc0a8ce40fe9d4d235f94d7ab1e7aba2ddafc`。工作范围为 OD-08 的
受控取证、确定性 Gate、本地独立签认与契约失效规则。当前为交付请审，
不等于 Advisor GO、Owner 阶段验收、main 合入或 V4 Alpha。

## 可核对的结果

| 证据 | 实际执行 | 边界 |
|---|---|---|
| [全量输出](regression/final/stdout.log)、[逐项日志](regression/final/stderr.log)、[运行记录](regression/final/result.json) | 232 项：229 pass、3 skip、0 failure/error；5 项外层探针通过 | 3 项原 direct 后端成功链仍跳过；单测中的 Fake/合成 Gate 不变成真实执行证明 |
| [代码绑定](COMMIT-BINDING.json) | 49 个受测输入前后未变，并逐字节匹配上述产品提交 | 限清单内 framework/schema/script/test/example/template；不宣称整个主机不变 |
| [质量作者证据](quality-author/README.md) | 11 场景真实 collector/Gate；日志、退出、超时、1 MiB 上限、文档检查、缺 receipt、自报成功和隔离边界 | 固定预审 Python stdio 入口；不证明测试设计充分或支持任意工具链 |
| [治理作者证据](governance-author/README.md) | 5 次真实取证、17 次 CLI：关键契约变化/恢复仍拒旧签认，再实际取证复签；同树、精确机械变更、偏离与基线失败分类 | 身份、契约和工作包均是公开合成 fixture；不是这些虚构主体对本产品的真实签认 |
| [非作者独立证据](independent/README.md) | 新 T/C 复跑质量链、独立中断反例和治理链；逐项结果见该目录 | 与作者分离的执行上下文；复用测试设计的部分明确标注；不冒称外部 Advisor 已运行 |

Gate 对真实失败输出 `failed`、不可验证输出 `unverifiable`；场景达到预期与
业务测试本身通过是两种计数。例如自报成功但实际退出 1 的场景验证成功，
其工程 Gate 仍是 failed。治理从实际受保护输入调用 Gate，不接受外部的
`status: passed` 文件作为依据，也不推进任务合入、部署或业务里程碑。

这里的全量是 install、protocol、local、bootstrap、quality、governance 六个
unittest 目录。V3 的 `p0_audit.py` 和锁定首轮设计假设的
`validate_v4_design.py` 本批未重新运行，不能将该计数理解为仓库所有历史脚本。
同一真实 bundle 的额外[重复验证](repeat-verification/result.json)与首次 Gate
逐字段完全一致，没有再次启动 collector。

## 修复与反例保留

- 原收集器读取祖先目录需要不必要的目录读取权限，已改为逐段 O_SEARCH /
  O_NOFOLLOW 固定目录描述符；没有放开祖先目录列表读取。早期错误日志保留。
- 仅清空子进程环境仍允许读取另一个进程的环境。独立探针只针对专门创建的
  无凭证合成进程，验证缺口和 `deny process-info* (target others)` 修复。
  收集器拒绝 fork，日志/输入/总时长有界；不把这些限定检查声称为完整沙盒安全证明。
- [初次全量回归](regression/initial/stderr.log) 的 local 组有 1 failure、5 error：
  原 `platform.system()` 调用被沙盒拒绝的 `os.uname()`。只把平台检测换成
  `sys.platform`，保留 sandbox-exec 存在检查，不放开 sysctl 权限。
  随后上述全量复跑通过。旧 PR #8 已审提交保持不动。
- 中断收集器后记录 unknown，不启动下一 case，保留 intent；相同 intent 重放
  不重新执行。突然崩溃后的未知进程自动接管仍未实现，不能从此反例外推。

## 如何读取和复跑

每个子目录保留协调器、固定输入、实际命令、退出和日志，索引分别记录原始
字节 SHA256 与公开脱敏副本 SHA256。只替换本机路径；原件保留在仓库之外。
路径替换会改变计划/日志的字节 hash，因此不能把公版文件的旧 pin 当作可直接
执行的信任配置。复跑须独立审核 collector 与入口，在新 T/C 重新建立真实 Git
对象、计划和操作方 pin，再执行各有限协调器的对应步骤。

固定 collector 独立预审字节：
`f4ad7874c7dc9415f4dc0d1d26f2d4d095b42ef7580b786152f0886452d9ab6f`。
候选 verifier/CLI 始终在实际沙盒内；宿主不导入候选模块。目录名、相邻 hash、
自报角色或不同模型都不自动建立信任。没有新增费用、供应商调用或长期服务。

仍待：外部 Advisor 对本次精确提交的评审，完整任务状态集成与 Lite 用户路径、
默认 direct 三项、真实双供应商/跨机/额度恢复，以及 Alpha/发布验收。failed Gate
不会因基线偏离自动豁免；本版只提供可核对的 known/new 分类和有证据的偏离关闭。
