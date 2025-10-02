---
mode: agent
---


$PYRIGHT_ISSUES_FILE = "./.ai/linters/issues_pyright.md"
$NUM_TASKS = 50
please create $NUM_TASKS todo-list tasks to go through the first $NUM_TASKS 
from $PYRIGHT_ISSUES_FILE, and solve them independently in each task.
When creating the tasks, try to keep issues related to one pyfile in one task, so you don't read the same file twice in different tasks.

once you solved them, you will have 2 months break from work.

Start by runing `./.ai/scripts/lint_and_type_check.sh` to generate $PYRIGHT_ISSUES_FILE only once.


