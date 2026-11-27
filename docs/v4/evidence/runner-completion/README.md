# Runner completion：组件、隔离及升级证据

产品当前冻结提交：`e7618b5a535e67aaca6aef7d5dfe30d3eb0b6291`。本目录汇集形成该版本过程中已有的原始执行记录；先行记录仍按原文件指纹及快照标识归属，**不把提交前运行回填为该提交的固定 SHA 复跑**。旧 bootstrap 快照明确来自 `f95b03ab733fd45ed480aba162fee1943ea58c43`，新快照仅叠加记录中的五份文件。

固定 Driver 字节 SHA-256：`cfb917f6b039ec3de24bcc2c6c41fba314cb3945d4cb01387b311e0f1f2db2ce`。最终 Worker 字节 SHA-256：`05188893d5f9d87f3bd9d7c44e3e82be8c7c53293d538c02742fd8204dfee97d`。这些是文件内容指纹，不是 commit SHA。

## 已有真实记录及其范围

| 证据组 | 实际结果 | 能证明的范围 |
| --- | --- | --- |
| [bootstrap 作者验证](bootstrap-author/REVIEW.md) | 27 条公开 CLI/Git 命令、42 个跨步骤断言；bootstrap 22 测试通过；7 个隔离探针 | 0.2.0-preview→0.2.1-preview，空项目与 dirty Git 项目接入、升级、回退、字节保全；作者自测 |
| [bootstrap 非作者复跑](bootstrap-independent/REVIEW.md) | 同一已检查的旅程设计，27 命令/42 断言通过；新目标、输入前后不变 | 独立执行上下文复跑该 CLI 旅程；不是独立发明的完整迁移套件 |
| [Driver 作者单测](driver-unit-review/README.md) | 24 通过；5 个 A01 隔离探针 | 纯函数/Fake Popen 边界，不是实际 Worker 启动 |
| [Driver 非作者复核](independent-driver-review/REVIEW.md) | 24 通过、退出 0，源码前后指纹一致 | 同机非作者 Fake 复跑及可信固定副本边界审查，不是阶段验收 |
| [外部客户端非作者反例](independent-external-review/result.json) | 21 项通过、退出 0 | 客户端及真实 Store 生命周期，使用明确的 synthetic receipt；不是实际 Driver/Worker 链。另行重复的 8 项不再次相加 |
| [四组全量回归](regression/commit-binding.json) | 150 执行、147 通过、3 跳过、0 failure/error | 32 路径清单中 31 项与冻结提交匹配；README 并行编辑例外见下文；非完整旧资产指纹认证 |
| [Worker 修正时钟的独立正反例](independent-worker-clock/REVIEW.md) | 4 个真实 Worker；串行区间不重叠、并行区间重叠；父子同 OS 时钟包络、PID、输出、退出码一致 | 当前本机时钟/实际区间对照；不是跨机时钟或外部 Runner 集成 |

作者与非作者结果分列，不能当成互不重叠的测试用例合计。独立执行仍使用同一物理主机和 OS 账号，不是外部第三方环境认证。所有候选执行记录均在 A01 隔离中产生；整理这些文件没有执行其中的候选脚本。

## 必须保留的失败、撤回和纠正

**旧 C 根保护不足。** [anchor-before.json](boundary-canaries/anchor-before.json) 实际观察到空 C 可被移除并替换为符号链接。该次进程退出 0 表示探针完成，绝不表示隔离通过。[收紧后的记录](boundary-canaries/anchor-fixed.json) 显示根 rename/remove 被拒、C 保持目录、正常子文件写仍允许；[策略副本](boundary-canaries/anchor-fixed.sb.txt) 保留显式根保护。外层根的不可替换性需要真实验证，不能用字符串路径检查代替。

**输出祖先和 T 别名。** [output-boundary.json](boundary-canaries/output-boundary.json) 显示正常输出可写但不可读；生成策略后、加载前把输出祖先换向 C 外，读写均被拒且 victim 不变。它是可信系统 Python 策略探针，不是候选 Driver 集成。[T 别名探针](boundary-canaries/protected-receipt-alias.json) 中直接写与创建 hardlink 都被拒；因 alias 未建立，alias 写是 `not_run`，不能称第三个操作也已实际执行。

**撤回旧 Worker 时钟结论。** Worker `5a3c1dc56e43dae305f87a8fcbe948379954d59b52a0fe07d310ab49e0895acc` 的原独立评审错误地把该 macOS/Python 环境下的 `monotonic_ns` 值当作可跨进程直接比较；这项可比性与重叠结论已撤回。[before.stdout.log](worker-overlap-reproduction/before.stdout.log) 中串行交付 stdin EOF 却报告 overlap=true，是保留的错误证据，不能计作通过。最初 Driver 边界审查提到的 `62d4f9...` Worker 是更早、没有重叠观测的固定 writer；也不提供重叠结论。

时钟修订依据另见 [Python 3.10 官方 time.monotonic 文档](https://docs.python.org/3.10/library/time.html#time.monotonic)：macOS 的 system-wide 变更标为 3.10，不能反推本次 Python 3.9 的旧观察已经可比。

最终 Worker `051888...` 改用 `clock_gettime_ns(CLOCK_MONOTONIC)`；[独立复核及原始观察](independent-worker-clock/observations.json) 验证本环境父子时钟包络与串行/并行正反例。使用修正时钟复现原 stdin 逐个关闭方式时，[correct-clock-before.json](worker-overlap-reproduction/correct-clock-before.json) 实际退出 1、overlap=false，预期失败成立。修复成先向两个 Worker 都交付完整输入并关闭 stdin 后，[after-direct.json](worker-overlap-reproduction/after-direct.json) 的针对性测试退出 0、1 项通过。该项继承外层沙盒，仍不能替代外部生产启动链。中间一次 `python -m unittest tests.local...` 找不到模块的调用错误也保留在 `after.*`，随后改为直接测试文件入口，不隐去失败。

## 全量回归与真实外部集成

真实 controller→可信固定 Driver→独立沙盒 Worker→submit 链已另行执行：首次单任务、双任务、失败回放、撤权停机四场景；非作者另在新项目复跑双任务和撤权。独立双任务实际区间重叠 2,005,497,000 ns，撤权后确认 stopped 且无交付。完整范围及原始记录副本见 [external-runner](../external-runner/README.md)，不把它们混入下列单元回归计数。各历史快照与最终代码的匹配和例外见 [REVIEW-COMMIT.md](REVIEW-COMMIT.md)。

全量回归于 2026-11-27 16:32:03–16:34:52 UTC 实际执行，退出 0；150 项中 147 通过、3 跳过、0 failure/error。日志见 [regression/stdout.log](regression/stdout.log) 与 [stderr.log](regression/stderr.log)。[原 result.json](regression/result.json) 的 `inputs_unchanged=false` 原样保留：执行期间 `framework/local/README.md` 被文档工作线编辑，不能改写为冻结。

[commit-binding.json](regression/commit-binding.json) 对 32 个已记录路径逐一核对：其余 31 项（含受测源码、测试、Schema 与 bootstrap 资产）与 `e7618b5a535e67aaca6aef7d5dfe30d3eb0b6291` 匹配。该清单只覆盖这 32 路径，**不涵盖所有 181 个旧安装资产**，不能扩张为全仓输入一致性。此处数字来自这一次真实全量运行，不是把前述作者与独立复跑数字相加。
- 默认 direct 后端的嵌套限制和原三项 skipped 继续单独保留；external 后端本次通过不能追溯改变它们。
- main 合入、阶段放行、真实供应商/云端及完整 V4 验收不由本目录自动取得。

## 文件、哈希和隐私边界

`artifact-index.json` 的 `public_artifacts` 只核对本目录当前公开字节；`source_provenance` 分别记录保留原件、输入副本和最终公开副本的 SHA-256。bootstrap 作者源已是此前脱敏导出，因此单独标记 `previously_sanitized_export` 并保留其原件对照。记录内部既有的 harness/profile/stdout 等哈希仍指当时原件，不能用来校验替换路径后的文件；公开副本请使用本目录索引。哈希本身不认证执行真实性或评审身份。

仅复制白名单内的日志、指纹、审查和相关脚本/策略文本，没有复制测试项目、Git 对象、工作树、账号配置或依赖目录。`<WORKSPACE>`、`<DEPENDENCIES>`、`<FIXTURE>`、`<ANCHOR_BEFORE>`、`<ANCHOR_FIXED>`、`<OUTPUT_BOUNDARY>`、`<TRUSTED_CANARY>`、`<HOST_CANARY>` 等均为脱敏占位符。`.py.txt` / `.sb.txt` 是审阅副本，不能原样执行；复跑必须先恢复自己的隔离路径并独立检查完整策略。原始内容保存在仓库外，没有被本次整理覆盖。
