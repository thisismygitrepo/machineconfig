
# gotch1: make sure we are in the right directory: repo root. Solution: check if .pyproject.toml exists, otherwise stop.
if [ ! -f "./pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in the current directory. Please run this script from the root of a Python project."
    exit 1
fi

mkdir -p .ai/linters || true

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
draw_progress $CURRENT_STEP $TOTAL_STEPS "Code Cleanup"
echo -e "${YELLOW}🧹 Cleaning and formatting code...${NC}"
uv run --frozen --with cleanpy -m cleanpy .
uv run --frozen --with ruff -m ruff clean
uv run --frozen --with ruff -m ruff check . --fix

mkdir -p .ai/linters

echo -e "${GREEN}🧹 Code cleanup complete!${NC}"
echo

draw_box "🔍 TYPE CHECKERS & LINTERS 🔍" "${BOLD}${PURPLE}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Pyright Type Checker"
echo -e "${BLUE}📋 Analyzing types with Pyright...${NC}"
rm -f ./.ai/linters/issues_pyright.md || true
uv run --frozen --with pyright pyright . > ./.ai/linters/issues_pyright.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.ai/linters/issues_pyright.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "MyPy Type Checker"
echo -e "${BLUE}📋 Analyzing types with MyPy...${NC}"
rm -f ./.ai/linters/issues_mypy.md || true
uv run --frozen --with mypy mypy . > ./.ai/linters/issues_mypy.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.ai/linters/issues_mypy.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Pylint Code Analysis"
echo -e "${BLUE}📋 Analyzing code quality with Pylint...${NC}"
rm -f ./.ai/linters/issues_pylint.md || true
uv run --frozen --with pylint pylint --recursive=y . > ./.ai/linters/issues_pylint.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.ai/linters/issues_pylint.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Pyrefly Type Checker"
echo -e "${BLUE}📋 Analyzing types with Pyrefly...${NC}"
rm -f ./.ai/linters/issues_pyrefly.md || true
uv run --frozen --with pyrefly pyrefly check . > ./.ai/linters/issues_pyrefly.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.ai/linters/issues_pyrefly.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Ty Type Checker"
echo -e "${BLUE}📋 Analyzing types with ty...${NC}"
rm -f ./.ai/linters/issues_ty.md || true
uv run --frozen --with ty ty check . > ./.ai/linters/issues_ty.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.ai/linters/issues_ty.md${NC}"

((CURRENT_STEP++))
draw_progress $CURRENT_STEP $TOTAL_STEPS "Ruff Linter"
echo -e "${BLUE}📋 Checking code style with Ruff...${NC}"
rm -f ./.ai/linters/issues_ruff.md || true
uv run --frozen --with ruff ruff check . > ./.ai/linters/issues_ruff.md
echo -e "${GREEN}✅ Results saved to ${UNDERLINE}./.ai/linters/issues_ruff.md${NC}"

echo
draw_box "🎉 ALL CHECKS COMPLETED! 🎉" "${BOLD}${GREEN}"
echo -e "${BOLD}${GREEN}📁 Check the ${UNDERLINE}.ai/linters${NC}${BOLD}${GREEN} directory for detailed results.${NC}"
