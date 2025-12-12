#!/bin/bash

# ============================================================
# init-claude-tools.sh
# AI 协作开发框架 - Claude Code 工具安装脚本
#
# 用法：
#   ./scripts/init-claude-tools.sh --target=/path/to/your-project
#   ./scripts/init-claude-tools.sh -t /path/to/your-project
#
# 功能：
#   将预置的 Slash Commands 安装到目标项目的 .claude/commands/ 目录
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 工具源目录
TOOLS_SOURCE="$PROJECT_ROOT/_templates/CC_COLLABORATION/05_TOOLS/slash-commands"

# 默认目标目录（当前目录）
TARGET_DIR=""

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

# 显示帮助信息
show_help() {
    cat << EOF
AI 协作开发框架 - Claude Code 工具安装脚本

用法:
    $0 [选项]

选项:
    -t, --target <path>    目标项目路径（必需）
    -h, --help             显示帮助信息
    -l, --list             列出可安装的工具
    -v, --verbose          显示详细输出

示例:
    $0 --target=/path/to/your-project
    $0 -t ~/my-project
    $0 --list

说明:
    此脚本将预置的 Slash Commands 复制到目标项目的 .claude/commands/ 目录。
    安装后，可在 Claude Code 中使用这些命令。

可用命令:
    /new-feature <name>     创建新功能模块
    /resume <feature>       断点恢复
    /daily-summary          生成每日总结
    /check-progress         查看进度状态
    /gen-demo <feature>     生成 Demo + Mock API
    /run-tests <feature>    执行测试
    /release <f> <v>        生成发布说明
    /init-project           初始化项目系统目录

EOF
}

# 列出可安装的工具
list_tools() {
    echo ""
    echo "可安装的 Slash Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ -d "$TOOLS_SOURCE" ]; then
        for file in "$TOOLS_SOURCE"/*.md; do
            if [ -f "$file" ]; then
                name=$(basename "$file" .md)
                echo "  /$name"
            fi
        done
    else
        print_error "工具源目录不存在: $TOOLS_SOURCE"
        exit 1
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
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

# 安装工具
install_tools() {
    local commands_dir="$TARGET_DIR/.claude/commands"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Claude Code 工具安装器"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    print_info "源目录: $TOOLS_SOURCE"
    print_info "目标目录: $commands_dir"
    echo ""

    # 检查源目录
    if [ ! -d "$TOOLS_SOURCE" ]; then
        print_error "工具源目录不存在: $TOOLS_SOURCE"
        exit 1
    fi

    # 创建目标目录
    if [ ! -d "$commands_dir" ]; then
        print_info "创建目录: $commands_dir"
        mkdir -p "$commands_dir"
    fi

    # 复制文件
    local count=0
    local skipped=0

    echo ""
    echo "安装 Slash Commands:"
    echo ""

    for file in "$TOOLS_SOURCE"/*.md; do
        if [ -f "$file" ]; then
            name=$(basename "$file")
            target_file="$commands_dir/$name"

            if [ -f "$target_file" ]; then
                if [ "$VERBOSE" = "1" ]; then
                    print_warning "跳过（已存在）: $name"
                fi
                ((skipped++))
            else
                cp "$file" "$target_file"
                print_success "安装: $name"
                ((count++))
            fi
        fi
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_success "安装完成！"
    echo ""
    echo "  新安装: $count 个"
    echo "  已跳过: $skipped 个"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "可用命令:"
    echo ""
    for file in "$commands_dir"/*.md; do
        if [ -f "$file" ]; then
            name=$(basename "$file" .md)
            echo "  /$name"
        fi
    done
    echo ""

    echo "下一步:"
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
