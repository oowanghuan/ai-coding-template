# 本地核心协议 0.1（WP-101）

`protocol.schema.json` 是 JSON Schema Draft 2020-12，根对象为一个本地声明快照；`$defs` 独立定义 Role、Provider、Host、Worker、Session、Work Package、Authorization、Assignment 和 Checkpoint。三种 Profile 共用同一格式；本批只接受 `local_git`，不部署尚待 OD-02 的 GitHub 控制分支。

`framework/core/protocol.py` 提供无写入、无联网、无调度的 `validate(snapshot, at)` 与 `validate_transition(before, after, at)`。同一输入和 UTC 时间得到相同排序错误。CLI：

```bash
# 在自己的隔离验证环境中显式安装 requirements-protocol.txt；本机实测使用已安装版本。
python3 scripts/validate_protocol.py examples/protocol/in-progress.json --at 2026-11-27T10:00:00Z
python3 scripts/validate_protocol.py after.json --before before.json --at 2026-11-27T10:00:00Z
```

成功退出 0，输入无效退出 2；未传 `--at` 使用当前 UTC 并在结果记录。示例是固定时间的合成数据，租约到期后用当前时间验证理应失败。重复 JSON 键和非 JSON 数值被拒绝。所有引用只解析本地 `$defs`，不启用网络 Schema 获取。使用方式依据 [jsonschema 验证 API](https://python-jsonschema.readthedocs.io/en/stable/validate/) 与 [离线 Registry](https://python-jsonschema.readthedocs.io/en/stable/referencing/)。

关键约束：

- 生命周期只有一个 `state`。类型分别要求不同里程碑；所有必需里程碑通过后才能 `accepted/closed`。代码合入不能代替工程验收或业务验证。
- 签认有对象 SHA、签认主体和非空证据引用；高风险任务要求实现者与评审/验收主体不同。主体来自显式登记，换模型不自动产生独立性。
- `ready/in_progress` 核对声明授权、期限、项目暂停/预算、依赖指定里程碑与版本。Active Assignment 还核对角色/Session/Host、期限、epoch、基线、并发、目录与文件范围冲突。
- Scope 只用字面文件或以 `/` 结尾的目录前缀；拒绝绝对路径、穿越和 glob。禁止范围从 Assignment 中保守排除，不能靠目录不同推断外部操作独立。
- 检查点保存规范、代码、未提交成果位置/指纹、已做/未做、未知操作与下一步。当前检查点含未知操作时不能继续声明开工。
- 迁移要求项目和变动 WP revision 增加；非法跨状态、降低风险、删减验收要求、重用已释放 Assignment、改变 Assignment 身份或不增加接管 token 均拒绝。签认后契约/交付等实质变更必须重新进入执行并失效旧签认。旧快照可能已有过期租约，因此迁移只要求其 Schema 有效，新快照必须通过当前语义检查，允许安全记录暂停。

**边界**：返回 valid 只表示输入声明内部一致，不能证明 Owner 真签过字、测试真运行、SHA 真存在、恢复文件可读取或身份真正独立。证据取证/验真归 WP-201/203；实际认领、锁和 fencing 执行归 WP-102；恢复操作归 WP-302；Ready Set 资源匹配及调度归 WP-401。本批不调用模型、不获得执行权，也不检查真实文件系统范围。

本批保守要求通过的各里程碑针对同一 submitted SHA；合入不同提交但相同受审树的证明留给 WP-203，不能先用文本说明绕过。状态验证不替代事件身份验证、CAS、追加日志、历史防篡改和风险策略服务。

合成 fixture 展示 canonical 机器字段，不是要求 Lite 用户手填这份 JSON。Lite 字段生成及最小人机路径仍由 WP-103/303 验证，不能把 Schema 完成称作可安装 V4 Alpha。
