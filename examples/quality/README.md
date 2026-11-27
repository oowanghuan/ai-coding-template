# 本地取证与 Gate 示例

本批提供有限的 Python 标准输入/输出检查适配器。它观察实际退出、输出、
超时和信号，再与预先批准的检查集合比较；不解析候选自写的“通过”报告。
完整字段见 [协议](../../framework/quality/CONTRACT.md)。运行依赖本机 macOS
Seatbelt 和系统 Python；其他系统无降级为不隔离执行的后备路径。

最小用例是把 `stdio_check.py` 和 `requirements.txt` 放入同一个真实 Git 提交的
只读 subject。文档检查 `required_heading` 返回 `present` 或实际失败；计算检查
`add` 返回结果。批准者事先确定每项输入、期待 stdout 的 UTF-8 字节 SHA256、
期待退出码、是否必需和超时。程序的自报结论不是 Gate 输入。

准备步骤由受信操作方完成，不能交给拥有候选修改权的进程自行批准：

1. 独立审核固定 collector 和检查入口，记录完整 SHA256；复制到受保护 T。
2. 从真实 Git 提交提取完整文件清单、模式、原始 commit body 和 tree，放入
   `T/subject`。同一 T 下存 `collector.py`、`plan.json`。C 与 T 分离。
3. 在候选无权写入或替换 T 的实际系统边界内，用批准 plan 的原始字节 hash
   调用固定 collector。它逐项建立独立沙盒，只允许对应 C 子目录写入。
4. 受信操作方将 run ID、T、plan/collector hash 和工作包版本登记到 trust；
   verifier 的 trust hash 从操作方受保护配置取得，不能从上传报告照抄。
5. 在候选隔离环境调用以下只读 CLI；同一组输入应给出完全相同结论。

```text
python3 scripts/v4_quality.py verify --trust /T/trust.json \
  --trust-sha256 <independently-pinned-raw-trust-hash> --run-id <registered-run-id>
```

这里没有自动安装可信收集器的脚本。目录名、相邻 hash 文件、当前账号或
另一模型的名字都不能建立可信边界。仓库内的 collector 还是候选代码时，
不得为了运行示例而直接在宿主执行它。操作方应先完成固定版本独立预审。

`passed` 只说明批准检查真实运行并满足结果，不证明检查设计完整，更不会
推进 merged、deployed 或 business_validated。必需项跳过、零实际检查、超时、
日志缺失、错 subject 或未知运行均不能通过。偏离只能由治理协议判断，不能
改写取证事实。SIGINT/未知结果后保留 intent 和日志，先对账再开始新运行。

这个目录是输入示例，不是已经运行的证据。实际运行与失败记录另列交付证据，
不得把示例输出、纯逻辑 fixture 或作者检查当作独立工程验收。
