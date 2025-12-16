#!/bin/bash

# ============================================================
# init-claude-tools.sh
# AI 协作开发框架 - Claude Code 工具安装脚本
#
# 用法：
#   ./scripts/init-claude-tools.sh --target=/path/to/your-project
#   ./scripts/init-claude-tools.sh -t /path/to/your-project
#   ./scripts/init-claude-tools.sh -t . --only=commands,skills
#
# 功能：
#   将预置的 Slash Commands、Skills、Subagents 安装到目标项目
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 工具源目录
TOOLS_BASE="$PROJECT_ROOT/CC_COLLABORATION/05_tools"
COMMANDS_SOURCE="$TOOLS_BASE/slash-commands"
SKILLS_SOURCE="$TOOLS_BASE/skills"
SUBAGENTS_SOURCE="$TOOLS_BASE/subagents"

# 默认目标目录
TARGET_DIR=""
VERBOSE=0

# 安装选项（默认全部安装）
INSTALL_COMMANDS=1
INSTALL_SKILLS=1
INSTALL_SUBAGENTS=1

# 统计变量
TOTAL_INSTALLED=0
TOTAL_SKIPPED=0

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "${CYAN}${BOLD}$1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
${BOLD}AI 协作开发框架 - Claude Code 工具安装脚本${NC}

${CYAN}用法:${NC}
    $0 [选项]

${CYAN}选项:${NC}
    -t, --target <path>    目标项目路径（必需）
    -o, --only <types>     只安装指定类型（逗号分隔）
                           可选值: commands, skills, subagents
    -h, --help             显示帮助信息
    -l, --list             列出可安装的工具
    -v, --verbose          显示详细输出

${CYAN}示例:${NC}
    $0 --target=/path/to/your-project          # 安装全部工具
    $0 -t ~/my-project                         # 安装全部工具
    $0 -t . --only=commands                    # 只安装 Slash Commands
    $0 -t . --only=commands,skills             # 安装 Commands 和 Skills
    $0 --list                                  # 列出所有可用工具

${CYAN}工具类型:${NC}
    ${BOLD}Slash Commands (10 个)${NC} → .claude/commands/
        用户直接调用的命令，如 /new-feature, /iresume 等

    ${BOLD}Skills (13 个)${NC} → .claude/skills/
        可复用的能力模块，如 progress_updater, ui_demo 等

    ${BOLD}Subagents (4 个)${NC} → .claude/subagents/
        处理复杂多步骤任务的子代理，如 spec_writer, test_plan_writer 等

EOF
}

# 列出可安装的工具
list_tools() {
    echo ""
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_header "  Claude Code 可安装工具列表"
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Slash Commands
    echo -e "${BOLD}📌 Slash Commands (→ .claude/commands/)${NC}"
    echo ""
    if [ -d "$COMMANDS_SOURCE" ]; then
        for file in "$COMMANDS_SOURCE"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                [ "$name" != "README" ] && echo "    /$name"
            fi
        done
    else
        print_error "    目录不存在: $COMMANDS_SOURCE"
    fi

    echo ""

    # Skills
    echo -e "${BOLD}🔧 Skills (→ .claude/skills/)${NC}"
    echo ""
    if [ -d "$SKILLS_SOURCE" ]; then
        for file in "$SKILLS_SOURCE"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                [ "$name" != "README" ] && echo "    $name"
            fi
        done
    else
        print_error "    目录不存在: $SKILLS_SOURCE"
    fi

    echo ""

    # Subagents
    echo -e "${BOLD}🤖 Subagents (→ .claude/subagents/)${NC}"
    echo ""
    if [ -d "$SUBAGENTS_SOURCE" ]; then
        for file in "$SUBAGENTS_SOURCE"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                [ "$name" != "README" ] && echo "    $name"
            fi
        done
    else
        print_error "    目录不存在: $SUBAGENTS_SOURCE"
    fi

    echo ""
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# 解析 --only 参数
parse_only_option() {
    local only_value="$1"

    # 重置所有安装标志
    INSTALL_COMMANDS=0
    INSTALL_SKILLS=0
    INSTALL_SUBAGENTS=0

    # 解析逗号分隔的值
    IFS=',' read -ra TYPES <<< "$only_value"
    for type in "${TYPES[@]}"; do
        case "$type" in
            commands)
                INSTALL_COMMANDS=1
                ;;
            skills)
                INSTALL_SKILLS=1
                ;;
            subagents)
                INSTALL_SUBAGENTS=1
                ;;
            *)
                print_error "未知工具类型: $type"
                echo "可选值: commands, skills, subagents"
                exit 1
                ;;
        esac
    done
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--target)
                TARGET_DIR="$2"
                shift 2
                ;;
            --target=*)
                TARGET_DIR="${1#*=}"
                shift
                ;;
            -o|--only)
                parse_only_option "$2"
                shift 2
                ;;
            --only=*)
                parse_only_option "${1#*=}"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                list_tools
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            *)
                print_error "未知选项: $1"
                echo "使用 -h 或 --help 查看帮助"
                exit 1
                ;;
        esac
    done
}

# 验证目标目录
validate_target() {
    if [ -z "$TARGET_DIR" ]; then
        print_error "请指定目标项目路径"
        echo ""
        echo "用法: $0 --target=/path/to/your-project"
        echo "使用 -h 查看更多选项"
        exit 1
    fi

    # 展开路径中的 ~
    TARGET_DIR="${TARGET_DIR/#\~/$HOME}"

    # 转换为绝对路径
    TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
        print_error "目标目录不存在: $TARGET_DIR"
        exit 1
    }

    # 检查是否是项目目录
    if [ ! -f "$TARGET_DIR/package.json" ] && [ ! -d "$TARGET_DIR/.git" ]; then
        print_warning "目标目录可能不是项目根目录（未找到 package.json 或 .git）"
        read -p "是否继续？[y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 安装单个工具类型
install_tool_type() {
    local source_dir="$1"
    local target_dir="$2"
    local tool_type="$3"
    local prefix="$4"  # 用于显示（如 "/" 或 ""）

    local count=0
    local skipped=0

    # 检查源目录
    if [ ! -d "$source_dir" ]; then
        print_error "$tool_type 源目录不存在: $source_dir"
        return 1
    fi

    # 创建目标目录
    if [ ! -d "$target_dir" ]; then
        if [ "$VERBOSE" = "1" ]; then
            print_info "创建目录: $target_dir"
        fi
        mkdir -p "$target_dir"
    fi

    # 复制文件
    for file in "$source_dir"/*.md; do
        if [ -f "$file" ]; then
            name=$(basename "$file")

            # 跳过 README.md
            if [ "$name" = "README.md" ]; then
                continue
            fi

            target_file="$target_dir/$name"
            display_name=$(basename "$file" .md)

            if [ -f "$target_file" ]; then
                if [ "$VERBOSE" = "1" ]; then
                    print_warning "跳过（已存在）: $prefix$display_name"
                fi
                ((skipped++))
            else
                cp "$file" "$target_file"
                print_success "安装: $prefix$display_name"
                ((count++))
            fi
        fi
    done

    # 更新全局统计
    TOTAL_INSTALLED=$((TOTAL_INSTALLED + count))
    TOTAL_SKIPPED=$((TOTAL_SKIPPED + skipped))

    echo "    新安装: $count 个，跳过: $skipped 个"
    echo ""
}

# 主安装函数
install_tools() {
    echo ""
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_header "  Claude Code 工具安装器"
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    print_info "目标项目: $TARGET_DIR"
    echo ""

    # 安装 Slash Commands
    if [ "$INSTALL_COMMANDS" = "1" ]; then
        echo -e "${BOLD}📌 安装 Slash Commands...${NC}"
        install_tool_type "$COMMANDS_SOURCE" "$TARGET_DIR/.claude/commands" "Slash Commands" "/"
    fi

    # 安装 Skills
    if [ "$INSTALL_SKILLS" = "1" ]; then
        echo -e "${BOLD}🔧 安装 Skills...${NC}"
        install_tool_type "$SKILLS_SOURCE" "$TARGET_DIR/.claude/skills" "Skills" ""
    fi

    # 安装 Subagents
    if [ "$INSTALL_SUBAGENTS" = "1" ]; then
        echo -e "${BOLD}🤖 安装 Subagents...${NC}"
        install_tool_type "$SUBAGENTS_SOURCE" "$TARGET_DIR/.claude/subagents" "Subagents" ""
    fi

    # 总结
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_success "安装完成！"
    echo ""
    echo "    总计安装: $TOTAL_INSTALLED 个"
    echo "    总计跳过: $TOTAL_SKIPPED 个"
    echo ""
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # 显示已安装的工具
    echo -e "${BOLD}已安装的工具:${NC}"
    echo ""

    if [ "$INSTALL_COMMANDS" = "1" ] && [ -d "$TARGET_DIR/.claude/commands" ]; then
        echo "  Slash Commands:"
        for file in "$TARGET_DIR/.claude/commands"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                echo "    /$name"
            fi
        done
        echo ""
    fi

    if [ "$INSTALL_SKILLS" = "1" ] && [ -d "$TARGET_DIR/.claude/skills" ]; then
        echo "  Skills:"
        for file in "$TARGET_DIR/.claude/skills"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                echo "    $name"
            fi
        done
        echo ""
    fi

    if [ "$INSTALL_SUBAGENTS" = "1" ] && [ -d "$TARGET_DIR/.claude/subagents" ]; then
        echo "  Subagents:"
        for file in "$TARGET_DIR/.claude/subagents"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                echo "    $name"
            fi
        done
        echo ""
    fi

    # 下一步提示
    echo -e "${BOLD}下一步:${NC}"
    echo ""
    echo "  1. 进入项目目录: cd $TARGET_DIR"
    echo "  2. 启动 Claude Code"
    echo "  3. 使用 /new-feature <name> 创建第一个功能模块"
    echo ""
}

# 主函数
main() {
    parse_args "$@"
    validate_target
    install_tools
}

# 执行主函数
main "$@"
