#!/bin/bash
set -e

# ─────────────────────────────────────────────────────
#  Obsidian Todo AI - 一键安装脚本
# ─────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

print_step() {
    echo ""
    echo -e "${CYAN}[$1/7]${NC} ${BOLD}$2${NC}"
}

print_ok() {
    echo -e "  ${GREEN}✅ $1${NC}"
}

print_warn() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
}

print_err() {
    echo -e "  ${RED}❌ $1${NC}"
}

echo ""
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo -e "${BOLD}   Obsidian Todo AI - 一键安装${NC}"
echo -e "${BOLD}═══════════════════════════════════════════${NC}"

# ── Step 1: 检查系统环境 ──────────────────────────────

print_step 1 "检查系统环境"

if [[ "$(uname)" != "Darwin" ]]; then
    print_err "此工具仅支持 macOS 系统"
    exit 1
fi
print_ok "macOS 系统"

if ! command -v python3 &> /dev/null; then
    print_err "未找到 python3，请先安装 Python 3.9+"
    echo "    推荐：brew install python3"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 9 ]]; then
    print_err "Python 版本 $PY_VERSION 过低，需要 3.9+"
    exit 1
fi
print_ok "Python $PY_VERSION"

# ── Step 2: 配置 Obsidian Vault 路径 ─────────────────

print_step 2 "配置 Obsidian Vault 路径"

DEFAULT_VAULT="$HOME/Documents/Obsidian Vault"

echo -e "  请输入你的 Obsidian Vault 路径"
echo -e "  ${YELLOW}（直接回车使用默认值：$DEFAULT_VAULT）${NC}"
read -r -p "  Vault 路径: " VAULT_PATH

if [[ -z "$VAULT_PATH" ]]; then
    VAULT_PATH="$DEFAULT_VAULT"
fi

VAULT_PATH="${VAULT_PATH/#\~/$HOME}"

if [[ ! -d "$VAULT_PATH" ]]; then
    echo -e "  目录不存在，是否自动创建？(y/n)"
    read -r -p "  " CREATE_VAULT
    if [[ "$CREATE_VAULT" == "y" || "$CREATE_VAULT" == "Y" ]]; then
        mkdir -p "$VAULT_PATH"
        print_ok "已创建 $VAULT_PATH"
    else
        print_err "Vault 目录不存在，安装中止"
        exit 1
    fi
else
    print_ok "Vault 路径：$VAULT_PATH"
fi

# ── Step 3: 配置 DeepSeek API Key ────────────────────

print_step 3 "配置 DeepSeek API Key"

echo -e "  请输入你的 DeepSeek API Key"
echo -e "  ${YELLOW}（直接回车跳过，后续可在 config.yaml 中补充）${NC}"
echo -e "  ${YELLOW}获取地址：https://platform.deepseek.com/${NC}"
read -r -p "  API Key: " API_KEY

if [[ -z "$API_KEY" ]]; then
    API_KEY=""
    print_warn "已跳过，每日任务将使用通用模板（无 AI 智能生成）"
else
    print_ok "API Key 已配置"
fi

# ── Step 4: 创建虚拟环境并安装依赖 ────────────────────

print_step 4 "创建虚拟环境并安装依赖（可能需要几分钟）"

cd "$PROJECT_DIR"

if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    print_ok "虚拟环境已创建"
else
    print_ok "虚拟环境已存在，跳过创建"
fi

source .venv/bin/activate
pip install --upgrade pip setuptools wheel -q 2>&1 | tail -1
pip install -e . -q 2>&1 | tail -1
print_ok "依赖安装完成"

# ── Step 5: 写入配置文件 ─────────────────────────────

print_step 5 "写入配置文件"

cat > "$PROJECT_DIR/config.yaml" << YAML
# Obsidian Todo AI 配置文件

# Obsidian Vault 路径
vault_path: "$VAULT_PATH"

# Todo 文件在 Vault 中的根目录
todo_root: "TodoList"

# DeepSeek AI 配置
ai:
  provider: "deepseek"
  api_key: "$API_KEY"
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"

# 定时任务配置
schedule:
  daily_run_time: "09:05"

# 用户偏好
preferences:
  language: "zh-CN"
  timezone: "Asia/Shanghai"
YAML

print_ok "配置文件已生成：config.yaml"

# ── Step 6: 初始化 Obsidian 目录结构 ──────────────────

print_step 6 "初始化 Obsidian 目录结构"

todo init
print_ok "目录结构已创建"

# ── Step 7: 注册每日定时任务 ──────────────────────────

print_step 7 "注册每日定时任务（每天 09:05 自动运行）"

PLIST_NAME="com.obsidian-todo-ai.daily"
PLIST_SRC="$PROJECT_DIR/$PLIST_NAME.plist"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

# 更新 plist 中的路径
cat > "$PLIST_SRC" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/scripts/daily_run.sh</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>5</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/launchd_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/launchd_stderr.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST

# 更新 daily_run.sh 中的路径
cat > "$PROJECT_DIR/scripts/daily_run.sh" << 'RUNSCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/daily_run.log"

mkdir -p "$PROJECT_DIR/logs"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG_FILE"

source "$PROJECT_DIR/.venv/bin/activate"
todo daily-run >> "$LOG_FILE" 2>&1

echo "Exit code: $?" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
RUNSCRIPT

chmod +x "$PROJECT_DIR/scripts/daily_run.sh"
mkdir -p "$PROJECT_DIR/logs"

if launchctl list | grep -q "$PLIST_NAME" 2>/dev/null; then
    launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

cp "$PLIST_SRC" "$PLIST_DST"
launchctl load "$PLIST_DST"
print_ok "定时任务已注册（每天 09:05）"

# ── 完成 ─────────────────────────────────────────────

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ 安装完成！${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BOLD}快速开始：${NC}"
echo ""
echo -e "    ${CYAN}cd $PROJECT_DIR${NC}"
echo -e "    ${CYAN}source .venv/bin/activate${NC}"
echo -e "    ${CYAN}todo today${NC}          # 查看今日任务"
echo -e "    ${CYAN}todo daily-run${NC}      # AI 生成今日任务"
echo -e "    ${CYAN}todo goal list${NC}      # 查看目标列表"
echo -e "    ${CYAN}todo --help${NC}         # 查看所有命令"
echo ""
echo -e "  ${BOLD}Obsidian 中查看：${NC}"
echo -e "    打开 Obsidian → 找到 ${CYAN}TodoList/${NC} 文件夹"
echo ""

if [[ -z "$API_KEY" ]]; then
    echo -e "  ${YELLOW}📝 提醒：你还没有配置 DeepSeek API Key${NC}"
    echo -e "  ${YELLOW}   编辑 $PROJECT_DIR/config.yaml 填入 api_key 即可启用 AI 功能${NC}"
    echo ""
fi
