# 显式 external Runner 的真实工程验证

受测产品提交：`e7618b5a535e67aaca6aef7d5dfe30d3eb0b6291`。本次验证 WP-102 的固定合成任务执行，不代表真实模型执行、独立 Evidence Gate、业务验收或整个 V4 完成。

候选控制器始终在无凭证、无网络、不能写 checkout 的外层沙盒中运行。已独立复核的有限启动器固定副本在受信侧执行，只能启动已固定哈希的 Worker；Worker 单独进入自己的沙盒。没有放开候选代码宿主执行，没有开启服务、创建模型会话或新增费用。原 `run` 后端的三项 nested Seatbelt skipped 保留；`run-external` 是本次实际验证的显式入口。

## 首次真实执行

四个独立临时项目分别验证以下链路，候选验证器与启动器均退出 0。负例的 Worker/CLI 非零是预期结果，不是把任务失败改写为成功。

| 场景 | 真实观测 |
|---|---|
| single | 实际 CLI → 请求 → 固定 Driver → 沙盒 Worker exit 0 → 受控交付；内容、baseline、assignment、epoch/token 匹配，`accepted: false` |
| parallel | 两个独立 Worktree、两份预先落地请求、两个实际 Worker；OS CLOCK_MONOTONIC 执行区间重叠 **1,998,892,000 ns**，两份内容不同的交付分别绑定正确执行权 |
| failure | 只读合成目标引发 Worker exit 1；首次与同键回放 CLI 均非零，权威状态/受保护 receipt 字节不变，不重复执行，不产生交付 |
| revoke | 观察真实 running receipt 后撤销执行权；固定 Driver 观察子进程 exit -15 后给 stopped，取消请求绑定原请求；不产生交付，同键回放不重启 |

各场景的实际隔离探针包括 T 直接写和硬链接、checkout 写、无关文件读写、空 C 根移除、网络连接均被 OS 拒绝；凭证变量不存在。macOS Python 在新的 C 中生成的指定 `xcrun_db` 被记录指纹后清理，随后才检验空根移除；其他条目不会被清理。记录见 [首次执行目录](author/README.md)。

## 独立执行与信任边界

独立上下文使用新的临时项目复跑，执行对象仍为同一产品提交。双任务的实际执行区间交集为 **2,005,497,000 ns**，两个 Worker 均 exit 0、两份交付 `accepted: false`。撤权场景核对 assignment=revoked、workspace=stopped、工作包=paused，真实退出已确认且无交付；两个场景候选验证器/Driver 均 exit 0、各 8 项隔离探针通过。独立结果及范围见 [独立记录](independent/README.md)；它们与首次执行分列，不与单元测试数字混加。

首次执行的受信取证器先检查规范路径、再打开末级文件，尚未防止检查与打开之间的祖先符号链接置换。首次固定合作 fixture 没有实施该攻击，真实结果保留，但不能将其称为敌意候选取证安全。独立取证器改为逐段目录 fd + O_NOFOLLOW，先复现原读者会读到无害外部标记，再验证拒绝换链、已固定父 fd 保持原文件、拒绝硬链接及 FIFO，才在新项目复跑。两版脚本和哈希分别保存，不覆盖原记录。

配置和日志的“可信”来自真实 OS 隔离与受信侧固定字节，不能由调用者把目录命名为 `trusted` 获得。控制器仍是已审查的合作控制器；CLI 的参数和 receipt 校验不等于对任意恶意控制器提供身份认证。未知启动或未确认停止保持未知，不通过旧 PID 杀进程，也不盲目再派发。

独立复核另以本次 Driver 真实生成的内层策略运行固定系统 Python 探针：T 配置/receipt、C 权威、checkout 的读写及网络共 9 项实际拒绝；只有自身 scratch 的唯一新 canary 可写，凭证环境缺席。原配置、receipt、源码、权威和日志字节前后未变。它验证该内层策略，未启动新的候选 Worker，见 [实际策略探针](independent/inner-policy-result.json)。

## 记录与剩余范围

公开副本替换本机路径，保留原文件哈希和公开副本哈希的区别；脚本 `.txt` 是审阅材料。原始日志、受保护 receipt 和临时成果保留在仓库外。各执行清单逐一与受测提交 Git blob 核对；后续受审提交只增加文档与证据，不改变已测产品字节。

本批仍不证明：默认 direct 成功链、完整未知进程自动恢复、新机器/双供应商接入、真实配额恢复、跨机与云端协作、完整 S01–S12、main 合入或发布。跨版本安装的独立证据和全量回归见 [runner-completion](../runner-completion/README.md)。
