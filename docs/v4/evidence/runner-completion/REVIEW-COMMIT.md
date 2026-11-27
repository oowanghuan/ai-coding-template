# 冻结提交证据对账（不是新增独立 Driver 签认）

对账对象：`e7618b5a535e67aaca6aef7d5dfe30d3eb0b6291`。

本次只读取该提交的 Git blob、现有执行记录、源指纹清单和公开策略副本，重新计算 SHA-256 并比对；没有运行候选或重复全量测试。**整理者编写了 Driver，因此不自称 Driver 的独立审核者。** Driver 的非作者边界审查与 24 项 Fake 复跑来自 [既有独立审查](independent-driver-review/REVIEW.md)；本报告仅整理和核验其清单与提交的对应关系。Worker 时钟独立结论来自 [修正后的独立复核](independent-worker-clock/REVIEW.md)。本报告不是 Owner 验收或阶段放行。

## 核心字节绑定

| 对象 | 冻结提交内实际 SHA-256 | 对应证据 |
| --- | --- | --- |
| `framework/local/launch_driver.py` | `cfb917f6b039ec3de24bcc2c6c41fba314cb3945d4cb01387b311e0f1f2db2ce` | 作者最终单测与独立 Driver 复跑均匹配 |
| `tests/local/test_launch_driver.py` | `815a62c123f68de3d9af282a7c3105a96415e71b957707afe23e3c878609a8a3` | 作者最终与独立复跑均匹配 |
| `framework/local/worker_process.py` | `05188893d5f9d87f3bd9d7c44e3e82be8c7c53293d538c02742fd8204dfee97d` | 修正时钟独立正负例匹配 |
| `framework/local/external.py` | `a96f448a659ee95e3718e876738d450cd7a422ffc1a9a0b70483677302f12d74` | 21 项独立客户端/Store 反例匹配 |
| `framework/local/README.md` | `339cb03fb93d0dd0415eb61370d87f48e4b52d7dd21c0b790ec034cf1084e7ce` | 是本次核对的部署说明；不同于运行期间旧文档指纹 |

## 清单对账结果

下列数目是**记录路径的字节匹配数**，不是测试通过数。所有成对 before/after 源映射也已核对一致；全量运行另有显式文档变动记录，不据此改写其原结果。

| 清单 | 对 e7618b5 的匹配 | 例外解释 |
| --- | ---: | --- |
| bootstrap 作者、独立旧快照，各 181 路径 | 各 174/181 | 两份旧快照的全部 181 路径另已逐项核对，均精确匹配声明的旧提交 f95b03；不应全部匹配新产品 |
| bootstrap 作者、独立五文件 overlay | 各 4/5 | `framework/local/README.md` 是 external 说明加入前的字节 |
| bootstrap 作者、独立实际新快照（旧清单叠加 overlay） | 各 178/182 | 新增 CLI 测试使总数为 182；4 个差异见下文，不能称其为全新产品提交快照 |
| Driver 最终作者清单 | 2/2 | 无例外 |
| Driver 独立清单 | 2/3 | Driver 和测试匹配；记录中的 Worker 为较早的固定 writer |
| external 独立清单 | 6/6 | external、两份测试、Store、direct runner、CLI 全匹配 |
| 修正时钟 Worker 清单 | 1/1 | 最终 `051888...` 匹配 |
| 全量回归清单 | 31/32 | 只差 `framework/local/README.md`；原 `inputs_unchanged=false` 保留 |
| Driver 三轮中间清单，各 2 路径 | 各 0/2 | 明确保留的作者迭代版本，不冒充最终版本结果 |

**旧快照的七个差异路径**：`examples/bootstrap/README.md`、`framework/local/README.md`、`framework/local/bootstrap.py`、`framework/local/worker_process.py`、`scripts/v4_local.py`、`templates/project/BOOTSTRAP.md`、`tests/local/test_local.py`。完整原指纹位于两份 [bootstrap input-manifest](bootstrap-author/input-manifest.json)。旧版本归属是 `f95b03ab733fd45ed480aba162fee1943ea58c43`，全部 181 项已按该提交核对，不是无来源的漂移。

**新 bootstrap 快照的四个差异路径**：`framework/local/README.md`、`framework/local/worker_process.py`、`scripts/v4_local.py`、`tests/local/test_local.py`。五文件 overlay 明确没有吸收并行 Runner 的源码/CLI/测试变更；该升级旅程用于验证 bootstrap 0.2.0→0.2.1，不能扩展为完整 external 后端测试。overlay 中 bootstrap 实现、guide、CLI 用例及 bootstrap 示例说明均与 e7618b5 匹配。

**README 例外**：bootstrap overlay 与全量输入记录保留的指纹为 `d1f1b4127b1d11b27db3a6f10345269473c506f5045c2bc1ef78b1bc99af7c03`，不等于冻结版本的 `339cb03...`。执行期间文档工作线增加 external 模式说明；[全量 commit-binding](regression/commit-binding.json) 已如实声明这一点。清单覆盖 32 路径，不能据此声称 181 个旧资产或全仓输入均在该次全量运行中被冻结。

**Driver 中间版本例外**（完整原值见各 result）：iteration-01 的 Driver `97befd91...` / 测试 `4ba3ff6c...`；iteration-02 的 Driver `4dbd5b31...` / 测试 `8401eea4...`；iteration-03 的 Driver `87ba48aa...` / 测试 `64cec627...`。这些记录只保留改进历史；最终 24 项结果对应上表 `cfb917...` / `815a62...`。

**Worker 历史版本与撤回**：独立 Driver 记录包含 `62d4f9a63ec66945965e8d874baf7d9f6f3bab5956990be44dcf8c22ba00804c`，是没有重叠观测的旧 writer。另一个曾使用 `monotonic_ns` 的版本 `5a3c1dc56e43dae305f87a8fcbe948379954d59b52a0fe07d310ab49e0895acc` 的跨进程可比性结论已撤回，不能把其串行假 overlap=true 视为通过。最终 `051888...` 的 `CLOCK_MONOTONIC` 正反例才是有效的新时钟证据。

部分针对性复现（例如 `worker-overlap-reproduction/after-direct.json`）只记录调用及退出码，没有独立记录完整受测源码哈希。它们可说明该次反例/修复观察，但不能单凭源文件路径宣称已经绑定 e7618b5；最终 Worker 绑定依赖独立 clock 清单，当前代码/测试绑定另见全量指纹。仓库外 harness、profile、日志、fixture 产物的 SHA-256 不是受测仓库代码指纹，不要求等于 Git blob；其原件/公开副本关系由本目录 artifact-index 分开记录。

## 已有反例范围与部署前提

Driver 的 24 项独立测试覆盖严格 JSON、固定程序/配置/请求、目录和别名拒绝、重复与 nested workspace、配置哈希、非阻塞 stdin、取消/超时、未知结果及重启不重发等，**使用 Fake Popen**。external 的 21 项独立用例覆盖缺失/伪造或回退 receipt、配置和进程绑定、取消不等于停止、撤权、旧操作不得换 backend/配置等，**使用 synthetic receipt 和真实 Store**。这些不是对真实 Driver 进程执行的替代验收。

冻结 README 对 C/T 的要求与当前设计及已保留策略探针一致：

- C 为控制器唯一可写夹具树；T 与 C 不交叠，配置/程序/receipt 不得由控制器改写。Worker 只写自身 scratch 与固定 output，不能改 receipt。它们是不同执行主体的权限，不能把“控制器对 T 只读”误解成禁止 Worker 自身 scratch 写入。
- C 根必须显式禁止 unlink/rename/替换。旧根保护失败已保留；收紧策略的真实 canary 拒绝根操作并允许子文件写，不能只靠不可写 parent。
- Worker output 权限要求 `require-all` 的 C 锚和固定 literal；不授予 workspace read。输出祖先换向 C 外的实测读写拒绝，和 README 前提一致。
- T-to-C hardlink 创建被拒，源字节不变；alias 写没有执行，不能说三个动作全部跑过。
- Driver 有限、固定程序与参数，无通用命令、凭证/网络扩权或常驻调度；取消只有观测退出后才可确认，未知结果不支持接管或盲重放。默认 direct 仍有三项 skipped。

上述是冻结实现/文档和**已提供组件与隔离记录**的一致性判断，不能从几份不同目录的 canary 拼出一个实际部署已经全链完成的结论。完整 C/T 实例的实际配置、程序副本、策略和进程/交付关联仍需由真实 integration 证据绑定。本次对账没有新增这样的执行证据，也没有扩大任何现有评审的范围。
