# 探测完成事件的类型准入

代码提交：`8901f4602b6588177a6ddc9e61520a10b838b8c5`。
在 OD-09 的原生 observer 接入准备中，补齐先前记录的低层输入缺口：
`probe-result.available` 缺失或非布尔值时，原来会按 false 消耗 pending 意图。
现在在任何内存、权威状态或 operation receipt 修改之前拒绝，保留未知请求。

- [作者复现](author/README.md)：新三项修复前 1 pass / 2 fail；修复后完整生命周期
  24 pass / 0 skip，登记输入不变，五项隔离探针通过。
- [非作者复跑](independent/README.md)：新隔离目录、六项隔离探针、冻结 28 个输入；
  生命周期 24 pass / 0 skip、输入不变。明确布尔 false/true 正例及原额度代数、预算、
  去重测试同时执行。相关输入绑定见 [COMMIT-BINDING.json](COMMIT-BINDING.json)。

本轮没有重跑无关的接管/演示或历史全量回归，不累加成一个更大的测试总数。
输入类型校验不认证供应商响应，也不证明请求实际完成。原生 observer 仍必须取得
真实完成证据，不能把未知结果转换成 false。全部 quota/probe 信号是合成夹具，
真实供应商调用为 0；不宣称自动额度恢复已通过。

原件在仓库外，公开副本分别列原始/脱敏指纹；前红、后绿和独立运行记录均保留。
