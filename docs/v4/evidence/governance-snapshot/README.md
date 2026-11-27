# Advisor 7226757604：锁定基线快照语义修订

回应 [Advisor 7226757604](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7226757604)
对 `9d05026208f18dff372300f149e5f1ae2007c1c2` 的评审。WP-201 固定 Python 入口
取证/Gate 获限定 GO；本次只处理 WP-203 目标引用保证的 REVISE 与授权记录来源。
修订代码提交为 `9df70b506dc109f3d4ff0d65332eefae0fff359d`。

## 修订与能力边界

评审指出的问题成立：原 verifier 比较 review、candidate 和锁定 policy 的
target_base_sha，没有读取真实 Git ref。三份旧输入一致时，实际目标分支前移
不会被识别；原有修改 candidate 字段的测试不足以证明实时有效性。

采用评审允许的收窄方案。所有 verify 结果（包括拒绝和错误路径）新增：

```json
{"verification_scope":"locked_baseline","current_target_status":"not_observed"}
```

两字段计入 decision_id。`effective` 与退出码 0 只表示锁定快照内的适用性；
它们不能用于断言当前目标有效或授权合入。CLI help、协议、示例和验收声明同步
说明该限制。没有新增实时观察器，也没有声称已完成 ref 新鲜度或合入前竞争检查。

## 实际验证

| 证据 | 本次实际执行 | 结论的限制 |
|---|---|---|
| [作者治理测试](unit/frozen-result.json)、[逐项输出](unit/frozen-stderr.log) | 32/32 pass，0 skip；三种结果、错误路径、decision_id、CLI help/JSON 和真实 Git 移动 | 单测中的成功 Gate 和身份为明确合成 fixture |
| [作者公开 CLI 记录](author/README.md) | 真实质量 CLI 重验既有收据；新临时 Git main 前移；同一治理 CLI 前后核验；新描述字段负例 | 复用先前真实质量取证，不运行 collector，不记作新增测试取证 |
| [非作者独立复跑](independent/README.md) | 新 Git/T 子目录/C；8 项沙盒探针；同 argv 前后完整 decision 一致；负例原因精确匹配 | 复用已审测试设计，真实执行目录独立；相同确定性 Git 对象 SHA 不表示复用同一目录 |

临时目标实际从 `b0d627cfbcb3413ac2d1880dff705a07ef2c5aae` 前移到
`a6c60c2c40b9ef06bd951db10e50b13134207467`，后者的父提交是前者。
协调器观察这些真实 Git 值并记录原始命令/输出；产品没有读取此 Git 项目的权限。
在原 review、signoff、candidate、trust 字节不变时，前后输出均明确限定快照，
且整个 decision 相同。另建 candidate 描述指向新 SHA 时，得到
`target-base-changed-recheck-required`；该负例仍然只是输入比较，不能冒充 ref 探测。

首次真实 CLI 实验因合成夹具缺少 Schema 要求的 contract，得到 unverifiable，
协调器整体退出 1；[作者目录](author/README.md)保留原始失败。随后只补夹具，
不更改产品或放宽 Schema，在新 stage/intent/Git 项目重新执行并通过。

本次运行的产品输入前后不变，并绑定上述代码提交。原受保护质量/治理文件
均逐指纹保全；新增 fixture 使用独占子目录。旧质量取证、原 232 项回归属于旧
受测提交，不将其改称本次重跑，也不把历史 3 项 direct skip 转成通过。

## 来源与公开性

所有身份、契约、临时 Git 内容都是公开合成 fixture，不能替代真实项目签认。
原始与路径脱敏后的 SHA256 分列索引；原件保留在仓库外。脱敏副本的旧 pin
不能直接当作新信任配置使用。候选 CLI 始终在 A01 沙盒内，宿主协调器只使用
已审核 stdlib 和固定 Git 命令，不导入候选模块、不合入本仓 main。

[OD-08](../../OWNER_DECISIONS.md#od-08本地证据门禁与签认治理批次) 同时更正：
Owner 的会话原话“继续？”与 Project Lead 的范围解释分开记录。公开可核对的
Owner 直接阶段裁定仍待确认，不用 Project Lead 的转述或本次 Advisor GO 代替。
本轮为已有交付的范围收窄修订，不扩大后续阶段。

仍待：本次精确交付 SHA 的外部复核、当前目标引用观察/新鲜度与合入前重检、
真实身份/任务集成、双供应商/恢复及 Alpha 验收。
