# WP-203 locked_baseline：作者真实目标分支移动验证

本包是实现协作方的作者验证，不代替独立评审。被验证的产品范围是**锁定基线快照**：读取受保护评审和质量证据，但不观察远端或本地目标分支的当前状态。`effective` 只针对锁定快照，不构成“现在可以安全合入”的证明。

## 有效运行

[第二次运行摘要](attempt-02/run/summary.json)为 `passed: true`；[实际执行](attempt-02/run/execute-invocation.json)退出 0。执行前核对协调器 SHA256 `e941a7ec74bc1fbd5818181fed75b84037fadb467194841405594249e2963137` 和 [7 文件产品 manifest](attempt-02/run/product-manifest.json)，后者原始 SHA256 为 `c493ff5cf69e942c2cd020f5c8babcf1f8c6a5fa35a5a2072afc0527d866d5cf`。

在**新建临时 Git 项目**中，固定 Git 命令真实推进 `refs/heads/main`：

| 观察 | 实际 SHA |
| --- | --- |
| 初始目标 | `b0d627cfbcb3413ac2d1880dff705a07ef2c5aae` |
| 推进后的目标 | `a6c60c2c40b9ef06bd951db10e50b13134207467` |
| 推进后提交的父提交 | `b0d627cfbcb3413ac2d1880dff705a07ef2c5aae` |

[Git 命令及实际输出](attempt-02/run/git-operations.json)、[初始 commit body](attempt-02/run/target-before.commit.txt)、[推进后 commit body](attempt-02/run/target-after.commit.txt)均保留。两个导出的真实 commit body 均按 Git 对象编码复算，与对应 SHA 相符。这些目标提交属于临时测试项目，**不是模板仓库的提交**。没有修改模板仓库的 main、配置或 Git 历史。

- [推进前](attempt-02/run/verify-before.json)与[推进后](attempt-02/run/verify-after-same-inputs.json)使用相同 CLI 参数及相同 candidate、review、signoff、policy、trust 字节。
- 两次均为 `effective`、`verification_scope: locked_baseline`、`current_target_status: not_observed`，完整 decision 相同。共同 `decision_id` 为 `c6d7ab347b6b61fe751f98337d40ec56ce446abdb6b7a56822b922ab6db79c5c`。
- 另写[新目标描述](attempt-02/candidate/candidate-new-target.json)，只将 `target_base_sha` 改成已推进 SHA，原 candidate 不变。[该负例](attempt-02/run/verify-new-target-descriptor.json)为 `rejected`，明确理由 `target-base-changed-recheck-required`，同时保留上述两项 scope 字段。
- [保留输入指纹](attempt-02/run/preserved-inputs.json)与摘要证明新受保护材料、原 candidate、既有 T 文件及产品输入均未改变。独立负例使用另一个文件，没有覆盖原描述。

目标分支状态由**受信测试协调器**用 Git 观察。产品 CLI 没有读取目标项目的能力，也未宣称观察过。实际[隔离探针](attempt-02/run/canary.json)还验证了目标 ref 文件不可读、T 写入与硬链接被拒、C 根删除被拒、外部及仓库写入被拒、网络被拒和凭证变量缺席。CLI 在仅 C 可写的 hardened Seatbelt 中运行；宿主协调器不导入候选模块。读取 C 的保留指纹使用逐级目录 fd、no-follow、普通单硬链接文件和大小上限。

## 首次失败保留

[第一次运行](attempt-01/run/summary.json)真实退出 1，`passed: false`。其合成 fixture 的 `required_contracts: []` 违反既有 Schema 的 `minItems: 1`，因此三次 governance verify 均为 `unverifiable`；即使临时分支已实际推进、两个决定相同，也不能作为目标场景通过。

[仅 fixture 的修正](attempt-02/run/fixture-fix.diff)新增固定合成 `SNAPSHOT` 契约文本、contract_owner 来源、同一版本及指纹的 review 引用、必需契约策略和依赖图。第二次使用全新 stage、intent、受保护材料、C 和临时 Git 项目，未改动产品源码或首次失败结果。该合成契约用于测试完整绑定，不是新增产品工程取证。

## 质量证据复用与身份边界

本轮**没有启动 collector，新 collector 执行次数为 0**。`reused-quality/` 保存之前真实运行的 success bundle 及其原始质量 trust 的公开副本；[质量 CLI 复核](attempt-02/run/quality-revalidation.json)是对该既有 receipt 的新只读验证，不是重新执行测试。既有受测合成对象 commit 为 `1761b52e88f4a9bf6a270dd50e61c2ddd6568ef0`，不得与上述临时目标 main 或模板产品提交混同。

新的 reviewer、acceptor、contract_owner 均为明确的合成 fixture 身份；其分工来自受保护配置。这不能证明现实组织人员的身份，也不代表 Owner 真实签认。产品只验证该受保护测试边界内的绑定关系。没有扩大到 live target 观测、合入、部署或业务验收。

## 原件、脱敏与索引

[SHA256-MANIFEST.json](SHA256-MANIFEST.json)列出 86 项记录的逐文件来源和公开路径：首次失败 35 项、第二次有效运行 37 项、复用质量材料 14 项。`original_sha256` 针对仓库外原始字节，`public_sha256` 针对本公开副本。个人与实验绝对路径已替换为 `/public/fixture/…`，原运行 hash 字段保留原值；**公开副本不直接满足原始 pin，不可把脱敏目录当作原运行目录重放**。

产品提交级绑定由本批主线材料提供。本包固定并记录的是实际受测 7 文件字节，未虚构其产品 commit SHA。原件保全于仓库外，公共文件完整性与隐私检查见 `PUBLIC-SHA256.json`、`PUBLIC-CHECK.json`。
