# WP-201 作者验证证据

本包由 Gate、Schema、CLI 和协调器的实现执行者整理，因此属于**作者验证**，不是独立验收。固定 collector 由另一实现者编写，并在宿主执行前经过非作者边界复核；该复核记录由对应独立证据包提供。本包没有替代独立评审或阶段放行。

## 实际执行与结果

[真实集成摘要](integration/summary.json)记录 2026-11-27 的首次完整执行：11 个场景均达到各自预期，协调器退出 0。这里“场景通过”包括正确拒绝负例，并不表示 11 份工程成果全部通过 Gate。

| 场景 | 实际执行或构造 | Gate 结论 |
| --- | --- | --- |
| success | UTF-8 输出退出 0；预期负向检查退出 3；一项获准可选 skip | passed |
| selfreport | 程序输出自称 passed 的 JSON，真实退出 1 | failed |
| timeout | 超时后观察到退出 -15 | failed |
| close-pipes | 程序先关闭输出管道，再睡眠；仍触发超时，观察退出 -15 | failed |
| flood | 实际输出超过 1 MiB；保留前缀恰好匹配预期 hash，但超限标志成立 | failed |
| requiredskip | 必测项明确跳过，没有 PID 或伪造退出码 | failed |
| empty | 零实际执行 | failed |
| document | 程序实际读取绑定于 Git 的 GUIDE.md，核对固定内容 | passed |
| fork | 实际尝试 fork，权限拒绝 | passed |
| forged-write | 实际程序尝试写 T、创建源文件硬链接、读写外部、联网、删除工作目录、读取唯一合成进程参数；生成 C 内假报告及配套 hash | passed：隔离检查成立 |
| no-collector | 专门构造 C 内假报告及配套 hash；**没有调用 collector，没有 T receipt** | unverifiable |

[重复调用](integration/replay.json)退出 2，重复调用前后的 T 文件集合与字节均未改变；[错误 trust pin](integration/success-gate-wrong-pin.json)被拒绝。[封存输入](integration/sealed-manifest.json)最终逐文件核对未变。

实际 stdout、stderr、PID、退出码、时间、policy 指纹与计数保存在 `trusted/<场景>/evidence.json` 及相邻 `logs/`、`policies/`。不为 no-collector 生成 receipt；没有执行的检查也不补造日志。[flood 原日志副本](trusted/flood/logs/flood.stdout)是从实际保留文件逐字节复制的 1,048,576 字节，不是通过重复字符重新生成。

每次 Gate CLI 均在外层 Seatbelt 中执行，仅允许写独立 C；T、仓库和依赖只读。实际外层 10 项探针覆盖 T 写入、T 硬链接、C 根删除、仓库写入、外部读写、网络、凭证变量缺席，以及系统信息访问拒绝和合成 marker 不可见。对应结果保存在 `integration/*-gate-*.json`。内层针对本次唯一 owned 合成进程的 `KERN_PROCARGS2` 观察为 `rc=-1 / errno=1`，marker 不可见，见 [boundary.stderr](trusted/forged-write/logs/boundary.stderr)。没有枚举或读取其他真实进程。该合成进程的实际退出 -15 已记录在[清理回执](integration/owned-canary-cleanup.json)。

## 固定源码及真实 Git 对象

真实测试对象是独立临时 Git 仓库中的合成 stdio 程序和文档，不是整个模板仓库：

- Commit：`e8f60e30700985ecee0f2b1640cdff24759d133b`
- Tree：`d5456ecfaab5520bcc12d2a1e02239b734dd8d80`
- [check.py](fixture/check.py)、[GUIDE.md](fixture/GUIDE.md)、[Git 原始 commit body](fixture/commit.raw)。后者来自真实 `git cat-file commit HEAD`，已与 plan 的原始 commit body 逐字节核对。
- collector 原始 SHA256：`f4ad7874c7dc9415f4dc0d1d26f2d4d095b42ef7580b786152f0886452d9ab6f`；固定副本保存在各场景的 `collector.py`。
- 受审协调器原始 SHA256：`8e6050e7eb4fe069b8d1601ec46ebde0a990aecbf86fc1bd2181af328d85be2e`；[公开源码副本](integration/coordinator.py)。

协调器只使用宿主 stdlib 和固定 Git 命令准备素材，不在宿主导入候选模块。宿主仅运行已独立审查并固定 hash 的 collector 副本；collector 将候选放入固定 Seatbelt/Python 适配器。prepare 保留唯一 owned PID 占位，execute 创建合成进程后、任何 collector 运行前，一次性封存该预定字段、plan、trust 和输入指纹。该有限权限不意味着任意仓库代码可在宿主执行。

## Gate 作者单元测试

这些测试使用**合成受保护 bundle fixture**验证 Gate 逻辑，不能证明其目录真的受 OS 保护，也不算实际 collector 执行证据。真实隔离与 collector 链的证据在前述集成场景中。

- [第 1 次 stdout](gate-unit/stdout-01.log)及[原始 stderr](gate-unit/stderr-01.log)：发现范围意外包含当时正在修改的 collector 测试，50 项中 45 pass、5 error；其中 Gate 37 项全部通过。5 个 error 为当时 collector 的祖先目录 `O_RDONLY` 与 A01 权限冲突。失败记录原样保留，不能称该次整组通过。
- [第 2 次](gate-unit/stdout-02.log)：限定 Gate，加入严格 JSON integer 与链接祖先检查后，39/39 通过。
- [最终第 3 次](gate-unit/stdout-03.log)：统一 16 MiB 单文件 / 64 MiB 总量、1024 文件、Git `S_IXUSR`、固定 `T/subject` 边界，增加目录和 mode 回归，**41/41 通过，0 skip**。5 项外层隔离探针全部通过；[受测四文件前后 hash](gate-unit/result-03.json)相同。

`tested-source/` 收录最终 41 项对应的 Gate、Schema、CLI、测试源码；没有把早期缺失的源码快照重建为历史原件。`gate-unit/harness.py` 是限定 Gate 后的最终脚本，适用于第 2、3 次；首次更宽发现范围可由原始日志确认，首次脚本字节没有单独存档。

## 公开副本及复核边界

本包共有 211 项复制或提取的记录，完整逐文件来源与目标见 [SHA256-MANIFEST.json](SHA256-MANIFEST.json)。源位置已映射到 `/public/fixture/…`；原件在仓库外保全。`original_sha256` 针对原始字节，`public_sha256` 针对本公开副本；未变化文件两值相同。嵌入 receipt、plan、trust 中的运行指纹仍保留原值，**脱敏副本不能直接满足原始 pin，也不是可直接重放的原运行目录**。协调器中的路径同样是审阅占位符。

这些结果限于本机 macOS Seatbelt 的有限 Python stdio 适配器与固定合成任务。Gate 不证明检查集充分、不抵抗宿主所有者篡改、不提供远程身份认证，不将通过检查自动升级成独立签认、合入、部署或业务验收。产品仓库提交身份应由本批主线的提交绑定材料提供，不能把上述 fixture commit 当作模板仓库 commit。
