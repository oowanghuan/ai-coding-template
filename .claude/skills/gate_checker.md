# gate_checker - Phase Gate 检查器

## 能力描述

检查指定功能模块的 Phase Gate 状态，验证是否满足进入下一阶段的条件。

**核心职责**：
- 检查 `required_outputs` 是否存在
- 执行 `quality_checks` 验证
- 检查 `approvals` 审批状态
- **检查 External Gate（Expert Review 结果）**
- 更新 `PHASE_GATE_STATUS.yaml` 的检查结果

**设计原则**：
- Gate 状态只能由此 skill 和 `/approve-gate` 命令写入
- 禁止手动修改 `gate_state` 字段
- **External Gate 优先级最高，不可被 Phase Gate 覆盖**

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称（如 `user-auth`） |
| phase | number/string | 是 | Phase 编号或名称（如 `1` 或 `kickoff`） |

## 输出

```yaml
gate_check_result:
  feature: "{feature-name}"
  phase: "phase_{n}_{name}"
  timestamp: "{datetime}"

  overall_state: pending | passed | blocked | skipped

  required_outputs:
    - path: "{file_path}"
      exists: true | false
      status: "✅ 存在" | "❌ 缺失" | "⏭️ 跳过（条件不满足）"

  quality_checks:
    - id: "{check_id}"
      passed: true | false
      severity: block | warn
      message: "✅ 通过" | "❌ 失败: {reason}" | "⚠️ 警告: {reason}"
      evidence:
        location: "{file}:{line}" | null
        matched: "{matched_content}" | null
        searched: ["{pattern1}", "{pattern2}"]  # 搜索失败时列出

  warnings:
    - id: "{check_id}"
      message: "⚠️ {warning_message}"

  approvals:
    required: ["{role1}", "{role2}"]
    completed:
      - role: "{role}"
        user: "{username}"
        at: "{datetime}"
    pending: ["{role}"]

  blocked_reasons:
    - "{reason1}"
    - "{reason2}"

  next_actions:
    - action: "{action_type}"
      description: "{action_description}"
      target_file: "{file}" | null
      role: "{role}" | null

  recommendation: |
    建议操作：
    1. {step1}
    2. {step2}
```

## 执行步骤

### 1. 读取配置和状态文件

```yaml
# 读取规则配置
config = load_yaml("docs/{feature}/PHASE_GATE.yaml")

# 读取运行状态
status = load_yaml("docs/{feature}/PHASE_GATE_STATUS.yaml")

# 获取 feature_profile（条件判断的事实源）
feature_profile = config.feature_profile
```

### 2. 解析 Phase 参数

```python
# 支持数字或名称
if phase is number:
    phase_key = f"phase_{phase}_*"  # 匹配 phase_1_kickoff 等
else:
    phase_key = f"phase_*_{phase}"  # 匹配 phase_1_kickoff 等

phase_config = config[phase_key]
phase_status = status[phase_key]
```

### 3. 检查阶段是否启用

```python
if "enabled_condition" in phase_config:
    if not eval_condition(phase_config.enabled_condition, feature_profile):
        return GateResult(
            state="skipped",
            reason="阶段已跳过（条件不满足）"
        )
```

### 4. 检查 required_outputs

```python
for output in phase_config.required_outputs:
    # 检查条件
    if "condition" in output:
        if not eval_condition(output.condition, feature_profile):
            results.append({
                path: output.path,
                exists: "skipped",
                status: f"⏭️ 跳过（条件不满足：{output.condition}）"
            })
            continue

    # 检查文件是否存在（支持 glob）
    matched_files = glob_match(output.path, feature_dir)

    if output.required and len(matched_files) == 0:
        blocked_reasons.append(f"缺少必需文件: {output.path}")
        results.append({
            path: output.path,
            exists: false,
            status: "❌ 缺失"
        })
    else:
        results.append({
            path: output.path,
            exists: true,
            status: "✅ 存在"
        })
```

### 5. 执行 quality_checks

```python
for check in phase_config.quality_checks:
    result = run_quality_check(check, feature_dir, feature_profile)

    if not result.passed:
        if check.severity == "block":
            blocked_reasons.append(f"质量检查失败: {check.description}")
        else:
            warnings.append({
                id: check.id,
                message: f"⚠️ {check.description}"
            })

    check_results.append(result)
```

#### 5.1 content_check 实现

```python
def run_content_check(check, feature_dir):
    target_files = glob_match(check.target, feature_dir)

    for file in target_files:
        content = read_file(file)

        # 搜索 anchor（正则匹配）
        matches = regex_findall(check.anchor, content)

        if len(matches) >= check.get("min_items", 1):
            return CheckResult(
                passed=True,
                evidence={
                    location: f"{file}:{line_number}",
                    matched: matches[0]
                }
            )

        # 检查 min_chars
        if "min_chars" in check:
            section_content = extract_section(content, check.anchor)
            if len(section_content) >= check.min_chars:
                return CheckResult(passed=True)

    return CheckResult(
        passed=False,
        evidence={
            location: None,
            searched: check.anchor.split("|")
        }
    )
```

#### 5.2 yaml_check 实现

```python
def run_yaml_check(check, feature_dir):
    target_file = glob_match(check.target, feature_dir)[0]
    yaml_data = load_yaml(target_file)

    # 使用字段路径获取值
    actual_value = get_nested_value(yaml_data, check.field)

    if actual_value == check.expected:
        return CheckResult(passed=True)
    else:
        return CheckResult(
            passed=False,
            message=f"字段 {check.field} 期望值为 {check.expected}，实际为 {actual_value}"
        )
```

#### 5.3 code_scan 实现

```python
def run_code_scan(check, feature_dir):
    # 在代码文件中搜索模式
    matches = grep_pattern(check.pattern, feature_dir, exclude=check.get("exclude", []))

    if len(matches) == 0:
        return CheckResult(passed=True)
    else:
        return CheckResult(
            passed=False,
            message=f"发现 {len(matches)} 处匹配: {check.pattern}",
            evidence={
                location: matches[0].file + ":" + matches[0].line,
                matched: matches[0].content
            }
        )
```

#### 5.4 manual 类型

```python
def run_manual_check(check, feature_dir):
    # manual 类型需要人工确认，始终返回 pending
    return CheckResult(
        passed=None,  # 未确认
        message="需要人工确认",
        checklist=check.get("checklist", [])
    )
```

#### 5.5 exec_check 实现（可执行命令检查）

**用途**：执行命令并验证结果，用于构建验证、脚本执行等场景。

**配置示例**：
```yaml
- id: build_success
  description: "项目必须能成功构建"
  type: exec_check
  command: "npm run build"
  working_dir: "_code"  # 相对于功能目录
  timeout: 120  # 秒
  success_criteria:
    exit_code: 0
    stdout_contains: "Build completed"  # 可选
    stderr_not_contains: "error"  # 可选
  severity: block
```

**实现**：
```python
def run_exec_check(check, feature_dir):
    """
    执行命令并验证结果

    安全边界：
    - working_dir 必须在 feature_dir 内
    - 命令必须在白名单内
    """
    # 安全检查：验证 working_dir
    working_dir = check.get("working_dir", ".")
    if ".." in working_dir:
        return CheckResult(
            passed=False,
            message="安全错误: working_dir 不能包含 .."
        )

    full_working_dir = os.path.join(feature_dir, working_dir)
    if not os.path.isdir(full_working_dir):
        return CheckResult(
            passed=False,
            message=f"工作目录不存在: {working_dir}"
        )

    # 安全检查：命令白名单
    command = check.command
    if not is_command_allowed(command):
        return CheckResult(
            passed=False,
            message=f"安全错误: 命令不在白名单内: {command}"
        )

    timeout = check.get("timeout", 60)

    try:
        # 使用 Bash 工具执行命令
        result = execute_bash(
            command=command,
            working_dir=full_working_dir,
            timeout=timeout
        )

        # 验证 exit_code
        criteria = check.get("success_criteria", {})
        expected_exit = criteria.get("exit_code", 0)

        if result.exit_code != expected_exit:
            return CheckResult(
                passed=False,
                message=f"命令退出码 {result.exit_code}，期望 {expected_exit}",
                evidence={
                    "command": command,
                    "exit_code": result.exit_code,
                    "stdout": result.stdout[-500:] if result.stdout else "",
                    "stderr": result.stderr[-500:] if result.stderr else ""
                }
            )

        # 验证 stdout_contains
        if "stdout_contains" in criteria:
            if criteria["stdout_contains"] not in (result.stdout or ""):
                return CheckResult(
                    passed=False,
                    message=f"输出不包含期望内容: {criteria['stdout_contains']}"
                )

        # 验证 stderr_not_contains
        if "stderr_not_contains" in criteria:
            if criteria["stderr_not_contains"] in (result.stderr or ""):
                return CheckResult(
                    passed=False,
                    message=f"错误输出包含禁止内容: {criteria['stderr_not_contains']}"
                )

        return CheckResult(
            passed=True,
            message="命令执行成功",
            evidence={
                "command": command,
                "exit_code": result.exit_code
            }
        )

    except TimeoutError:
        return CheckResult(
            passed=False,
            message=f"命令超时 ({timeout}s)"
        )
    except Exception as e:
        return CheckResult(
            passed=False,
            message=f"执行失败: {str(e)}"
        )

def is_command_allowed(command):
    """
    检查命令是否在白名单内

    白名单模式：
    - "npm run *"
    - "npm test"
    - "python3 -m http.server *"
    - "pytest *"
    - "vitest *"
    - "jest *"
    - "cargo test"
    - "go test *"
    """
    import fnmatch

    allowed_patterns = [
        "npm run *",
        "npm test",
        "npm test *",
        "python3 -m http.server *",
        "python -m http.server *",
        "pytest",
        "pytest *",
        "vitest",
        "vitest *",
        "jest",
        "jest *",
        "cargo test",
        "cargo test *",
        "go test",
        "go test *",
        "npx *",
        "node *",
    ]

    # 黑名单检查
    blocked_patterns = [
        "*rm -rf*",
        "*sudo *",
        "*curl * | *sh*",
        "*> /dev/*",
        "*chmod 777*",
        "*eval *",
    ]

    for blocked in blocked_patterns:
        if fnmatch.fnmatch(command, blocked):
            return False

    for pattern in allowed_patterns:
        if fnmatch.fnmatch(command, pattern):
            return True

    return False
```

#### 5.6 test_check 实现（测试执行检查）

**用途**：执行测试命令并解析测试结果，验证测试通过率。

**配置示例**：
```yaml
- id: unit_tests_pass
  description: "单元测试必须全部通过"
  type: test_check
  command: "npm test"
  working_dir: "_code"
  timeout: 300
  success_criteria:
    exit_code: 0
    parse_format: "jest"  # jest | vitest | pytest | generic
    min_pass_rate: 100  # 百分比
    allow_skip: false
  severity: block
```

**实现**：
```python
def run_test_check(check, feature_dir):
    """
    执行测试命令并解析结果
    """
    # 首先执行命令
    exec_result = run_exec_check(check, feature_dir)

    # 如果命令执行失败，直接返回
    if not exec_result.passed:
        return exec_result

    # 解析测试输出
    stdout = exec_result.evidence.get("stdout", "")
    parse_format = check.get("success_criteria", {}).get("parse_format", "generic")

    test_result = parse_test_output(stdout, parse_format)

    # 验证通过率
    criteria = check.get("success_criteria", {})
    min_pass_rate = criteria.get("min_pass_rate", 100)
    allow_skip = criteria.get("allow_skip", True)

    if test_result["pass_rate"] < min_pass_rate:
        return CheckResult(
            passed=False,
            message=f"测试通过率 {test_result['pass_rate']:.1f}% < {min_pass_rate}%",
            evidence={
                "passed": test_result["passed"],
                "failed": test_result["failed"],
                "skipped": test_result["skipped"],
                "total": test_result["total"],
                "pass_rate": test_result["pass_rate"]
            }
        )

    if not allow_skip and test_result["skipped"] > 0:
        return CheckResult(
            passed=False,
            message=f"存在 {test_result['skipped']} 个跳过的测试",
            evidence=test_result
        )

    return CheckResult(
        passed=True,
        message=f"测试通过: {test_result['passed']}/{test_result['total']}",
        evidence=test_result
    )

def parse_test_output(stdout, format):
    """
    解析测试输出

    支持格式：
    - jest: "Tests: X passed, Y failed, Z total"
    - vitest: 类似 jest
    - pytest: "X passed, Y failed"
    - generic: 尝试通用解析
    """
    import re

    result = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "total": 0,
        "pass_rate": 0
    }

    if format == "jest" or format == "vitest":
        # Jest/Vitest: "Tests: 5 passed, 2 failed, 7 total"
        match = re.search(r"Tests:\s+(\d+)\s+passed.*?(\d+)\s+failed.*?(\d+)\s+total", stdout)
        if match:
            result["passed"] = int(match.group(1))
            result["failed"] = int(match.group(2))
            result["total"] = int(match.group(3))

        # 检查 skipped
        skip_match = re.search(r"(\d+)\s+skipped", stdout)
        if skip_match:
            result["skipped"] = int(skip_match.group(1))

    elif format == "pytest":
        # Pytest: "5 passed, 2 failed in 1.23s"
        match = re.search(r"(\d+)\s+passed", stdout)
        if match:
            result["passed"] = int(match.group(1))

        match = re.search(r"(\d+)\s+failed", stdout)
        if match:
            result["failed"] = int(match.group(1))

        match = re.search(r"(\d+)\s+skipped", stdout)
        if match:
            result["skipped"] = int(match.group(1))

        result["total"] = result["passed"] + result["failed"] + result["skipped"]

    else:  # generic
        # 尝试通用解析
        pass_match = re.search(r"(\d+)\s*(passed|pass|ok|success)", stdout, re.I)
        fail_match = re.search(r"(\d+)\s*(failed|fail|error)", stdout, re.I)

        if pass_match:
            result["passed"] = int(pass_match.group(1))
        if fail_match:
            result["failed"] = int(fail_match.group(1))

        result["total"] = result["passed"] + result["failed"]

    # 计算通过率
    if result["total"] > 0:
        result["pass_rate"] = (result["passed"] / result["total"]) * 100

    return result
```

#### 5.7 serve_check 实现（服务启动检查）

**用途**：启动服务并执行健康检查，验证服务是否正常运行。

**配置示例**：
```yaml
- id: demo_runs
  description: "Demo 必须可正常运行"
  type: serve_check
  command: "python3 -m http.server 8889"
  working_dir: "_demos"
  startup_timeout: 5  # 等待启动的秒数
  health_check:
    url: "http://localhost:8889/login-demo.html"
    method: GET
    expected_status: 200
    timeout: 10
  severity: block
```

**实现**：
```python
def run_serve_check(check, feature_dir):
    """
    启动服务并验证健康检查

    流程：
    1. 后台启动服务
    2. 等待启动
    3. 执行健康检查
    4. 关闭服务
    """
    # 安全检查
    working_dir = check.get("working_dir", ".")
    if ".." in working_dir:
        return CheckResult(
            passed=False,
            message="安全错误: working_dir 不能包含 .."
        )

    full_working_dir = os.path.join(feature_dir, working_dir)
    command = check.command

    if not is_command_allowed(command):
        return CheckResult(
            passed=False,
            message=f"安全错误: 命令不在白名单内: {command}"
        )

    startup_timeout = check.get("startup_timeout", 5)
    health = check.get("health_check", {})

    # 启动后台进程
    process = start_background_process(
        command=command,
        working_dir=full_working_dir
    )

    try:
        # 等待启动
        import time
        time.sleep(startup_timeout)

        # 检查进程是否还在运行
        if process.poll() is not None:
            return CheckResult(
                passed=False,
                message="服务启动失败，进程已退出",
                evidence={
                    "exit_code": process.returncode
                }
            )

        # 执行健康检查
        health_url = health.get("url")
        if not health_url:
            return CheckResult(
                passed=False,
                message="未配置 health_check.url"
            )

        expected_status = health.get("expected_status", 200)
        health_timeout = health.get("timeout", 10)

        try:
            # 使用 WebFetch 或 curl 执行健康检查
            response = http_get(health_url, timeout=health_timeout)

            if response.status_code == expected_status:
                return CheckResult(
                    passed=True,
                    message=f"服务启动成功，健康检查通过 (HTTP {response.status_code})",
                    evidence={
                        "url": health_url,
                        "status_code": response.status_code
                    }
                )
            else:
                return CheckResult(
                    passed=False,
                    message=f"健康检查失败: HTTP {response.status_code}，期望 {expected_status}",
                    evidence={
                        "url": health_url,
                        "status_code": response.status_code
                    }
                )

        except Exception as e:
            return CheckResult(
                passed=False,
                message=f"健康检查请求失败: {str(e)}",
                evidence={
                    "url": health_url,
                    "error": str(e)
                }
            )

    finally:
        # 清理：终止进程
        terminate_process(process)
```

#### 5.8 e2e_check 实现（端到端测试检查）

**用途**：执行端到端浏览器测试，验证完整用户流程。

**配置示例**：
```yaml
- id: e2e_login_flow
  description: "登录流程端到端测试"
  type: e2e_check
  serve:  # 可选：启动服务
    command: "python3 -m http.server 8889"
    working_dir: "_demos"
    startup_timeout: 3
  steps:
    - action: navigate
      url: "http://localhost:8889/login-demo.html"
    - action: wait
      seconds: 1
    - action: assert
      type: element_exists
      selector: "[data-testid='email']"
    - action: fill
      selector: "[data-testid='email']"
      value: "test@example.com"
    - action: fill
      selector: "[data-testid='password']"
      value: "password123"
    - action: click
      selector: "[data-testid='submit']"
    - action: wait
      seconds: 2
    - action: assert
      type: url_contains
      value: "dashboard"
  severity: block
```

**实现**：
```python
def run_e2e_check(check, feature_dir):
    """
    执行端到端测试（使用 MCP 浏览器工具）

    流程：
    1. 启动服务（如果配置了）
    2. 创建浏览器标签页
    3. 执行测试步骤
    4. 清理资源
    """
    serve_process = None

    try:
        # 1. 启动服务（如果配置了）
        if "serve" in check:
            serve_config = check["serve"]
            working_dir = os.path.join(feature_dir, serve_config.get("working_dir", "."))

            serve_process = start_background_process(
                command=serve_config["command"],
                working_dir=working_dir
            )

            import time
            time.sleep(serve_config.get("startup_timeout", 3))

        # 2. 获取浏览器标签页上下文
        tab_context = get_browser_tab_context()
        tab_id = create_browser_tab()

        # 3. 执行测试步骤
        steps = check.get("steps", [])

        for i, step in enumerate(steps):
            result = execute_e2e_step(step, tab_id)

            if not result.success:
                return CheckResult(
                    passed=False,
                    message=f"E2E 步骤 {i+1} 失败: {step['action']}",
                    evidence={
                        "step_index": i,
                        "step": step,
                        "error": result.error
                    }
                )

        return CheckResult(
            passed=True,
            message=f"E2E 测试通过 ({len(steps)} 步骤)",
            evidence={
                "steps_executed": len(steps)
            }
        )

    finally:
        # 4. 清理资源
        if serve_process:
            terminate_process(serve_process)

def execute_e2e_step(step, tab_id):
    """
    执行单个 E2E 测试步骤

    支持的 action：
    - navigate: 导航到 URL
    - wait: 等待指定秒数
    - click: 点击元素
    - fill: 填写表单
    - assert: 断言
    """
    action = step.get("action")

    if action == "navigate":
        # 使用 MCP navigate 工具
        return mcp_navigate(tab_id, step["url"])

    elif action == "wait":
        import time
        time.sleep(step.get("seconds", 1))
        return StepResult(success=True)

    elif action == "click":
        # 使用 MCP find + click 工具
        selector = step["selector"]
        elements = mcp_find(tab_id, selector)
        if not elements:
            return StepResult(success=False, error=f"未找到元素: {selector}")
        return mcp_click(tab_id, elements[0])

    elif action == "fill":
        # 使用 MCP form_input 工具
        selector = step["selector"]
        value = step["value"]
        elements = mcp_find(tab_id, selector)
        if not elements:
            return StepResult(success=False, error=f"未找到元素: {selector}")
        return mcp_form_input(tab_id, elements[0], value)

    elif action == "assert":
        return execute_e2e_assertion(step, tab_id)

    else:
        return StepResult(success=False, error=f"未知的 action: {action}")

def execute_e2e_assertion(step, tab_id):
    """
    执行 E2E 断言

    支持的断言类型：
    - element_exists: 元素存在
    - element_not_exists: 元素不存在
    - url_contains: URL 包含
    - text_contains: 文本包含
    """
    assert_type = step.get("type")

    if assert_type == "element_exists":
        selector = step["selector"]
        elements = mcp_find(tab_id, selector)
        if elements:
            return StepResult(success=True)
        return StepResult(success=False, error=f"元素不存在: {selector}")

    elif assert_type == "element_not_exists":
        selector = step["selector"]
        elements = mcp_find(tab_id, selector)
        if not elements:
            return StepResult(success=True)
        return StepResult(success=False, error=f"元素不应存在但存在: {selector}")

    elif assert_type == "url_contains":
        # 获取当前 URL
        current_url = mcp_get_current_url(tab_id)
        expected = step["value"]
        if expected in current_url:
            return StepResult(success=True)
        return StepResult(success=False, error=f"URL 不包含 '{expected}'，当前: {current_url}")

    elif assert_type == "text_contains":
        page_text = mcp_get_page_text(tab_id)
        expected = step["value"]
        if expected in page_text:
            return StepResult(success=True)
        return StepResult(success=False, error=f"页面不包含文本: {expected}")

    else:
        return StepResult(success=False, error=f"未知的断言类型: {assert_type}")
```

### 5.9 安全边界配置

**命令白名单**：

```python
ALLOWED_COMMAND_PATTERNS = [
    "npm run *",
    "npm test",
    "npm test *",
    "python3 -m http.server *",
    "python -m http.server *",
    "pytest",
    "pytest *",
    "vitest",
    "vitest *",
    "jest",
    "jest *",
    "cargo test",
    "cargo test *",
    "go test",
    "go test *",
    "npx *",
    "node *",
]

BLOCKED_COMMAND_PATTERNS = [
    "*rm -rf*",
    "*sudo *",
    "*curl * | *sh*",
    "*wget * | *sh*",
    "*> /dev/*",
    "*chmod 777*",
    "*eval *",
    "*exec *",
]
```

**工作目录限制**：
- `working_dir` 必须相对于功能目录
- 禁止使用 `..` 跳出功能目录
- 禁止使用绝对路径

### 6. 检查审批状态

```python
required_roles = phase_config.approvals.required_roles
completed_approvals = [
    a for a in phase_status.approvals
    if a.user is not None
]
completed_roles = [a.role for a in completed_approvals]
pending_roles = [r for r in required_roles if r not in completed_roles]

if pending_roles:
    return GateResult(
        state="pending",
        reason=f"等待审批: {', '.join(pending_roles)}"
    )
```

### 7. 检查 External Gate（Expert Review）

**硬规则**：External Gate 的 BLOCK 优先级最高，不可被 Phase Gate 覆盖。

```python
def check_external_gate(feature_dir):
    """
    检查 External Gate（Expert Review 结果）

    返回：
    - status: 'not_applicable' | 'passed' | 'blocked'
    - reason: 结构化原因对象
    """
    actions_file = f"{feature_dir}/REVIEW_ACTIONS.yaml"

    # 如果文件不存在，不适用
    if not exists(actions_file):
        return {
            "status": "not_applicable",
            "reason": None
        }

    actions = load_yaml(actions_file)

    # 检查 verdict
    if actions.verdict == "BLOCK":
        # 检查是否有有效的 override
        if is_override_valid(actions.get("override", {})):
            return {
                "status": "passed",
                "reason": {
                    "type": "override_approved",
                    "approved_by": actions.override.approved_by,
                    "approved_at": actions.override.approved_at
                }
            }

        # 返回结构化 reason（用于 UI / Agent / Progress Log 消费）
        return {
            "status": "blocked",
            "reason": {
                "type": "external_review_block",
                "source": "expert_reviewer",
                "block_count": actions.summary.block_count,
                "warn_count": actions.summary.warn_count,
                "reference": "REVIEW_REPORT.md",
                "actions_file": "REVIEW_ACTIONS.yaml"
            }
        }

    # GO 或 REVISE 都视为通过
    return {
        "status": "passed",
        "reason": None
    }

def is_override_valid(override):
    """
    检查 override 是否有效

    规则：
    - override.enabled == true
    - override.approved_by 不为空
    - override.expires_at 未过期（或为空表示不过期）
    """
    if not override.get("enabled", False):
        return False
    if not override.get("approved_by"):
        return False
    if override.get("expires_at"):
        if parse_datetime(override.expires_at) < now():
            return False
    return True
```

**在计算最终状态前检查 External Gate**：

```python
# 先检查 External Gate
external_gate_result = check_external_gate(feature_dir)

if external_gate_result["status"] == "blocked":
    # External Gate 阻断优先级最高
    blocked_reasons.insert(0, "External Gate (Expert Review) 阻断")
    external_gate_blocked = True
else:
    external_gate_blocked = False
```

### 8. 计算最终状态

```python
# External Gate 阻断优先级最高
if external_gate_blocked:
    overall_state = "blocked"
elif blocked_reasons:
    overall_state = "blocked"
elif pending_roles:
    overall_state = "pending"
else:
    overall_state = "passed"
```

### 9. 更新 PHASE_GATE_STATUS.yaml

```python
# 只更新 last_check，不直接设置 gate_state（除非是 blocked）
phase_status.last_check = {
    checked_at: current_datetime,
    blocked_reason: blocked_reasons[0] if blocked_reasons else None,
    check_results: check_results
}

# 如果是 blocked，更新 gate_state
if overall_state == "blocked":
    phase_status.gate_state = "blocked"
    phase_status.gate_state_meta = {
        last_updated_at: current_datetime,
        last_updated_by_command: "gate_checker",
        last_updated_by_user: null
    }

# 追加到 check_history
phase_status.check_history.append({
    checked_at: current_datetime,
    result: overall_state,
    blocked_reasons: blocked_reasons
})

# 保存文件
save_yaml(status, "docs/{feature}/PHASE_GATE_STATUS.yaml")
```

### 10. 生成 next_actions

```python
next_actions = []

for reason in blocked_reasons:
    if "缺少必需文件" in reason:
        next_actions.append({
            action: "create_file",
            description: f"创建缺失的文件: {extract_path(reason)}",
            target_file: extract_path(reason)
        })
    elif "质量检查失败" in reason:
        next_actions.append({
            action: "fix_content",
            description: reason,
            target_file: related_file
        })

for role in pending_roles:
    next_actions.append({
        action: "request_approval",
        description: f"请 {role} 审批",
        role: role
    })
```

### 11. 输出结果

输出结构化的检查结果，格式参见「输出」部分。

**External Gate 被阻断时的输出**：

```
📋 Phase Gate 检查结果

功能模块: {feature}
阶段: Phase {N} {Name}
检查时间: {datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ❌ BLOCKED (External Gate)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚫 External Gate (Expert Review) 阻断

Block 级问题: {block_count}
Warn 级问题: {warn_count}

查看详情：
  • docs/{feature}/REVIEW_ACTIONS.yaml
  • docs/{feature}/REVIEW_REPORT.md

📝 下一步操作:
  1. 修复所有 block 级问题
  2. 重新执行评审：/expert-review {feature}
  3. 或申请 override（需要说明理由）
```

## 输出示例

### 示例 1：Gate 被阻断

```
📋 Phase Gate 检查结果

功能模块: user-auth
阶段: Phase 2 Spec
检查时间: 2024-12-15T11:00:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ❌ BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 必需产出物:
  ✅ 21_UI_FLOW_SPEC.md - 存在

📊 质量检查:
  ✅ spec_has_pages - SPEC 包含页面定义
     └─ 位置: 21_UI_FLOW_SPEC.md:15
     └─ 匹配: "## 1. 登录页面"
  ❌ spec_has_error_cases - SPEC 未定义错误处理
     └─ 搜索: ["错误处理", "Error", "异常"]
  ⚠️ spec_has_edge_cases - 建议补充边界条件

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T10:00:00)
  ⏳ Architect: 待审批

🚫 阻断原因:
  1. 质量检查失败: SPEC 未定义错误处理

📝 建议操作:
  1. 在 21_UI_FLOW_SPEC.md 中添加「## 错误处理」章节
  2. 请 Architect 审批
```

### 示例 2：Gate 通过

```
📋 Phase Gate 检查结果

功能模块: user-auth
阶段: Phase 1 Kickoff
检查时间: 2024-12-15T10:30:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ✅ PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 必需产出物:
  ✅ 10_CONTEXT.md - 存在
  ✅ 90_PROGRESS_LOG.yaml - 存在

📊 质量检查:
  ✅ context_has_goals - 包含功能目标 (3 条)
  ✅ context_has_non_goals - 包含 Non-Goals (2 条)
  ✅ context_has_acceptance - 包含验收标准 (120 字符)

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T10:00:00)

🎉 Gate 已通过，可以进入下一阶段！
```

## 注意事项

1. **只读原则**：此 skill 只更新 `PHASE_GATE_STATUS.yaml`，不修改其他文件
2. **安全写入**：`gate_state` 只能设置为 `blocked`，`passed` 需要通过 `/approve-gate` 设置
3. **条件解析**：使用安全的表达式解释器，不执行任意代码
4. **Glob 匹配**：`*` 只匹配根目录，`**` 才递归子目录
5. **幂等性**：多次运行相同检查应产生相同结果

## 关联工具

- `/check-gate` - 调用此 skill 显示 Gate 状态
- `/approve-gate` - 在此 skill 检查通过后记录审批
- `/next-phase` - 在执行前调用此 skill 验证
- `/expert-review` - 执行 External Gate 评审
- `expert_reviewer` - External Gate 评审 Subagent
- `progress_updater` - 协同更新进度信息
