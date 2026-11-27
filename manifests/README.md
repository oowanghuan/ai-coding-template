# V3 工具兼容清单

`v3-tools.json` 是 WP-001 的唯一安装清单：26 Commands、21 Skills（其中 15 个仅存在于历史安装目录）、5 Subagents，以及这些工具引用的 98 个 `CC_COLLABORATION` 文件。

每个入口记录 canonical source、安装目标、SHA256 和已知 Skills 依赖。五个不同内容的旧安装命令以 `preserved_copies` 保留原字节及语义裁定，不再将它们当成第二份可自由修改的源。安装使用清单中的 canonical source。已有项目遇到不同副本会报告冲突，不会自动覆盖。更新源文件时须同步评审 manifest 指纹；缺源、缺依赖、漂移均失败。

本批明确修改旧安装脚本和四个源命令的失效引用；基线原件保存在 `legacy/v3.3.0/`。其余历史 Skills、安装副本、GUI 资产不删除。`check-gate` 保留指向旧 `gate_checker` 的兼容说明，但不把旧文档检查称为可信工程证据 Gate。

这仍是 V3 prompt definitions 的安装兼容层。没有安装 `settings.json`、Hooks、登录配置或 GUI；没有宣称当前供应商会原生发现 `.claude/skills/*.md` 或 `.claude/subagents/*.md`。当前 CLI 格式适配归 WP-301。

```bash
bash scripts/init-claude-tools.sh --list
bash scripts/init-claude-tools.sh --target /path/to/existing-empty-directory --dry-run
bash scripts/init-claude-tools.sh --target /path/to/existing-empty-directory
bash scripts/init-claude-tools.sh --target /path/to/existing-empty-directory --rollback TRANSACTION_ID
```

需要 Python 3.9+ 和 POSIX `fcntl`。`--only commands` 会带上声明的 Skills 依赖与框架资源。未指定 `--target` 不默认写当前目录。原有 `-t/-o/-l/-v` 保留，`-v` 目前不增加输出；安装结果始终是 JSON。

安装前全量检查冲突；成功后留下 `.ai-coding-template/transactions/` 收据。相同输入重复安装不创建新事务。回退只移除本次创建且未被改动的文件；用户改动、符号链接、结果未知的中断写入均保留并报错。重复回退旧收据不会误删后来重新安装的文件。

单实例锁只协调使用本安装器的同机进程，不抵御恶意并发文件系统替换，不是跨机器锁或沙盒。进程在文件写入与收据之间崩溃时，需要先核对实际文件和 planned/created 清单，不能盲目继续。完整项目 init/import/upgrade 属 WP-103。
