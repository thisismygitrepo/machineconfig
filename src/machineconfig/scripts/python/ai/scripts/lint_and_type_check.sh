
# gotch1: make sure we are in the right directory: repo root. Solution: check if .pyproject.toml exists, otherwise stop.
if [ ! -f "./pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in the current directory. Please run this script from the root of a Python project."
    exit 1
fi

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
NC='\033[0m' # No Color

# Box drawing functions
draw_box() {
    local text="$1"
    local color="$2"
    local width=60
    local padding=$(( (width - ${#text}) / 2 ))
    local line=""
    for ((i=0; i<width; i++)); do line="${line}─"; done
    
    echo -e "${color}┌${line}┐${NC}"
    printf "${color}│%*s%s%*s│${NC}\n" $padding "" "$text" $padding ""
    echo -e "${color}└${line}┘${NC}"
}

draw_progress() {
    local current="$1"
    local total="$2"
    local description="$3"
    echo -e "${CYAN}┌────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} ${BOLD}${WHITE}Step ${current}/${total}:${NC} ${description}${CYAN}$(printf '%*s' $((50 - ${#description} - 8)) "")│${NC}"
    echo -e "${CYAN}└────────────────────────────────────────────────────────────┘${NC}"
}

TOTAL_STEPS=7
CURRENT_STEP=0

draw_box "🚀 LINTING & TYPE CHECKING SUITE 🚀" "${BOLD}${CYAN}"
echo

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Environment Setup"
echo -e "${BLUE}🔧 Installing and updating development dependencies...${NC}"
# uv add pylint pyright mypy pyrefly ruff ty --dev  # linters and type checkers
# uv add --dev cleanpy pylint pyright mypy pyrefly --upgrade-package cleanpy pylint pyright mypy pyrefly
uv add --dev pyright --upgrade-package pyright
uv add --dev pylint --upgrade-package pylint
uv add --dev mypy --upgrade-package mypy
uv add --dev pyrefly --upgrade-package pyrefly
uv add --dev cleanpy --upgrade-package cleanpy

uv add types-requests types-toml types-PyYAML types-pytz types-paramiko types-urllib3 --dev
uv add types-mysqlclient types-SQLAlchemy --dev

echo -e "${GREEN}✅ Environment setup complete!${NC}"
echo

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Code Cleanup"
echo -e "${YELLOW}🧹 Cleaning and formatting code...${NC}"
uv run -m cleanpy .
uv run -m ruff clean
# uv run -m ruff format .
uv run -m ruff check . --fix
uv run --no-dev --project $HOME/code/machineconfig -m machineconfig.scripts.python.ai.generate_files

mkdir .linters

echo -e "${GREEN}🧹 Code cleanup complete!${NC}"
echo

draw_box "🔍 TYPE CHECKERS & LINTERS 🔍" "${BOLD}${PURPLE}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Pyright Type Checker"
echo -e "${BLUE}📋 Analyzing types with Pyright...${NC}"
rm ./.linters/pyright_result.md || true
uv run pyright . > ./.linters/pyright_result.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.linters/pyright_result.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "MyPy Type Checker"
echo -e "${BLUE}📋 Analyzing types with MyPy...${NC}"
rm ./.linters/mypy_result.md || true
uv run mypy . > ./.linters/mypy_result.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.linters/mypy_result.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Pylint Code Analysis"
echo -e "${BLUE}📋 Analyzing code quality with Pylint...${NC}"
rm ./.linters/pylint_result.md || true
uv run pylint ./src/ > ./.linters/pylint_result.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.linters/pylint_result.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Pyrefly Type Checker"
echo -e "${BLUE}📋 Analyzing types with Pyrefly...${NC}"
rm ./.linters/pyrefly_result.md || true
uv run pyrefly check . > ./.linters/pyrefly_result.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.linters/pyrefly_result.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Ruff Linter"
echo -e "${BLUE}📋 Checking code style with Ruff...${NC}"
rm ./.linters/ruff_result.md || true
uv run ruff check . > ./.linters/ruff_result.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.linters/ruff_result.md${NC}"

echo
draw_box "🎉 ALL CHECKS COMPLETED! 🎉" "${BOLD}${GREEN}"
echo -e "${BOLD}${GREEN}📁 Check the ${UNDERLINE}.linters${NC}${BOLD}${GREEN} directory for detailed results.${NC}"
