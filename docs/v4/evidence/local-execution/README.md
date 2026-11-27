# OD-07 / WP-102/103 实施与接手证据

测试代码提交：`e56449e0b05fab06a34453792f4cca2d9323f1b1`。计划基线为 `228e9d6e4ca326b3f73c31686e4312a842d00c52`；首批依赖仍为 `673d6baa13283180b342f446bcadc17ad66efaf9`。本目录随后以纯文档提交附加，不改测试对象。状态是实现预览、待独立评审和工程验收，不是两个 WP 完整 accepted。

## 人工接手与自动链路断点

已读 [OD-07 7218268841](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7218268841)、跟进 7218308159 和澄清 7218355739；[接手回执 7219186379](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7219186379) 明确本次由 Owner 在现有 Codex 会话人工提醒触发，非自动投递。

第一断点为 **pending 识别 → 向既有会话投递**。已部署 broker 没有该调用或已验证消费者；没有前台核查后的 outbox 就等待。裁定中的计划 SHA 和依赖 SHA 产生 unbound 待核对键，不是未授权开工。原始输入、运行日志与运维 journal 留在仓库外，公开仅取与该事件相关的运行摘要。

| UTC 自然轮询 | 评论数 | pending | processed | 最后成功步骤 / 结局 |
|---|---:|---:|---:|---|
| 12:40 | 27 | 1 | 0 | 等待前台核查后的回复；未投递到会话 |
| 12:55 | 27 | 1 | 0 | 同一事件仍等待 |
| 13:10 | 27 | 1 | 0 | 同一事件仍等待 |
| 13:25 | 28 | 0 | 0 | complete；读到人工接手回执后去重 |
| 13:40 | 28 | 0 | 0 | complete；下一轮仍未重复处理 |

对应 `poll-<run_id>.json` 保留时间、步骤与 broker 指纹。后两轮证明评论匹配/补读去重，不证明自动唤醒或接单。没有新增无人值守模型执行、候选宿主执行、网络权限或付费服务。

## 固定提交隔离测试

macOS 15.5 arm64 / Python 3.9.6，使用已安装的固定协议依赖。外层 Seatbelt 禁止网络、凭证/宿主文件读取及 checkout 写入，只允许一次性夹具目录写入。环境按白名单重建；候选没有发布认证。`test-result.json` 保存实际提交、时间、命令、全部相关输入指纹、退出码和执行前后文件一致性（true）。

| 测试组 | 执行计数（含 skipped） | 通过 | 失败/错误 | skipped |
|---|---:|---:|---:|---:|
| install 旧安装回归 | 23 | 23 | 0 | 0 |
| protocol 旧协议回归 | 34 | 34 | 0 | 0 |
| local 新状态/执行测试 | 24 | 21 | 0 | 3 |
| bootstrap 新安装测试 | 17 | 17 | 0 | 0 |
| 合计 | 98 | 95 | 0 | 3 |

命令为 `sandbox-exec -f <isolated-run>/next-sandbox.sb <system-python> -B -S <isolated-run>/run_next_tests.py <isolated-run>/config.json`，退出 0。`V4_OUTER_SEATBELT=1` 仅描述实际外层隔离环境，不是开启沙盒的开关。入口快照为 `run-tests.py.txt`，外层策略为 `outer-sandbox.sb.txt`；复跑者须审查并将占位路径替换为自己的隔离目录、只读 checkout 和依赖。不能移除外层保护以强行取消 skipped。

实测包括真实子进程同时认领仅一个成功、原子提交后 `os._exit` 中断及新进程重读、同键回放/异意图拒绝、过期认领换 token、旧 epoch/token/被撤权交付拒绝、范围/容量/授权/依赖阻断；真实两个进程在不同 Worktree 同时运行固定合成任务、各自捕获交付而根目录不变。后者继承外层测试沙盒，**没有经过生产 Runner 的内层启动链**。

安装实测覆盖空项目、脏 Git/未跟踪成果/定制规则保全、只读预演、陈旧计划拒绝、幂等应用、追加升级与回退、状态进展不可回退覆盖、未知写入保全、安装/回退最终回执丢失的对账。结果文件/日志不是 WP-201 已实现的可信证据 Gate；这里是受控的作者测试记录。

## 失败、跳过与单独沙盒验证

`iteration-01.*.log` 保留首次新 local 组 19 项中 2 failure / 2 error：内层 `sandbox_apply: Operation not permitted`，以及外层尚未允许父进程给自身子进程发终止信号。旧 57 项当时通过。该次来自未提交的迭代源码，不冒充固定 SHA 复跑结果。

外层策略仅补充 `(allow signal (target children))`，允许故障清理终止自己创建的子进程；未开放网络、宿主文件写入或任意进程信号。macOS 的嵌套 Seatbelt 初始化限制仍存在，生产 Runner 没有退回裸执行。新增用例核实其退出 71、没有输出和采纳成果。`iteration-02.*.log` 是中间迭代记录；最终以固定 SHA 的 `tests.*.log` 为准。

三项 skipped：完整 Runner 单任务交付、完整 Runner 双任务并行、内层策略探针。前两项成功链仍待独立隔离主机/虚拟机复跑。策略与固定 Worker 另由外层可信工具直接启动一次 Seatbelt，避免嵌套，也不在宿主直接执行候选 Python：策略先在外层隔离中生成，再人工核查许可路径后启动。`standalone-result.json`、`worker-sandbox.sb.txt`、`standalone-probe.py.txt` 和四份 standalone 日志记录该次执行。

该独立进程实测退出 0，写入预定文件；六项探针证实宿主 canary 读/写、checkout 写、非授权输出路径、网络均拒绝，凭证环境不存在。Worker 产物指纹为 `91db8d2ff4e4f7c33475a487096bb3ca2c3e2100609db93b4ba314e7c120b344`。只证明 Worker/策略单独有效，不回填完整父控制器启动链的 skipped。

## 公开处理与未完成事项

`artifact-index.json` 同时记录原始和公开副本指纹。日志仅替换 workspace、依赖、临时夹具和无害 canary 的绝对路径；原始文件保留在仓库外。测试对象文件指纹不变。没有私有研究、凭证、客户信息或其他项目资料。

- 完整 Runner 成功链、独立非作者故障复跑和工程验收未完成；Advisor 静态 GO 也不能代替这些证据。
- 进程启动后硬崩溃/设备重启未知结果只冻结保全，未提供自动确认已停止及接管；完整恢复仍待后续协议。
- Bootstrap 不提供活跃任务编辑、授权生成或真实供应商适配；完整 Lite 用户路径未验收。
- 真实 Codex 会话自动投递/接单、跨机/云端、完整 S01–S12、main 合入和发布均未完成。

以上缺口交由同一 Draft PR 继续核查，不请求 Owner 重复批准已授权的普通修订。
