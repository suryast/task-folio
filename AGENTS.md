# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work atomically
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**
```bash
# Force overwrite without prompting
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` - use `-o BatchMode=yes` for non-interactive
- `ssh` - use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` - use `-y` flag
- `brew` - use `HOMEBREW_NO_AUTO_UPDATE=1` env var

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs with git:

- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-- END BEADS INTEGRATION -->

## Task Tracking (MANDATORY)
- Use `bd ready` to find next actionable tasks
- `bd update <id> --claim` before starting work
- `bd update <id> --status closed` when done
- Never work on tasks without claiming them first
- Check `bd list` to avoid conflicts with other agents

## Personal Risk Profiler

TaskFolio includes a local personal risk profiler. You can run it interactively in the terminal (`cd scripts && python3 -m profiler`) or drive it conversationally via chat as described below.

### Data
- Dataset: `public/data/pipeline/output/tasks_cache.json` (6,690 tasks, 361 occupations)
- Each task: `id`, `description`, `automation_pct`, `augmentation_pct`, `timeframe`, `occupation_title`, `anzsco_code`
- Occupations use ANZSCO codes (Australian) with O*NET crosswalk

### Chat-Based Profiling (Cursor, Claude Code, Copilot Chat, etc.)

When a user asks you to analyse their job or run the profiler through chat, **do NOT run the CLI**. Instead, drive the conversation interactively:

#### Step 1: Ask for their job title
> "What's your job title or role?"

Then search for matches:
```python
import sys; sys.path.insert(0, "scripts")
from profiler.occupation_search import load_occupations, search_occupations
matches = search_occupations(load_occupations(), "<user's answer>")
```

Present the top matches and ask them to pick one:
> "I found these matches:
> 1. Software Engineer (ANZSCO 2613)
> 2. Software Tester (ANZSCO 2614)
> Which one fits best?"

#### Step 2: Show their tasks and ask which ones they do
```python
from profiler.questionnaire import get_tasks_for_occupation
tasks = get_tasks_for_occupation("<chosen anzsco_code>")
```

Present ALL tasks as a numbered list and ask:
> "Here are the 18 tasks for Software Engineer. Which ones do you actually do? Give me the numbers (e.g. 1, 3, 5, 7, 12)."

**Do not assume.** Let the user pick. If they say "all of them" — use all tasks.

#### Step 3: Ask about time allocation
> "How do you split your time across those tasks? Rough percentages are fine (they should add up to ~100%).
> For example: '1: 30%, 3: 20%, 5: 20%, 7: 15%, 12: 15%'"

If they say "roughly equal" — split evenly.

#### Step 4: Build profile and show results
```python
from profiler.questionnaire import build_profile, calculate_personalised_score

selections = {
    tasks[0]["id"]: {"does_task": True, "time_pct": 30},
    tasks[2]["id"]: {"does_task": True, "time_pct": 20},
    # ... etc based on user's answers
}
profile = build_profile("<anzsco_code>", selections)
profile["score"] = calculate_personalised_score(profile)
```

Present the results conversationally:
- Overall exposure score with risk level (🟢 LOW / 🟡 MEDIUM / 🔴 HIGH)
- Automation risk vs augmentation potential
- Timeline breakdown (which tasks are affected now vs later)
- Per-task breakdown showing which specific tasks are most at risk

#### Step 5: Offer to save reports
```python
from profiler.report import generate_markdown, generate_html
md = generate_markdown(profile)
html = generate_html(profile)
# Save to scripts/reports/<slug>-report.md and .html
```

> "Want me to save a detailed report? I can generate Markdown and a self-contained HTML page."

### Key Rules for Chat Agents
1. **Always ask — never assume** which tasks the user does or how they split time
2. **Show all available tasks** so the user can pick (don't filter or pre-select)
3. **Be conversational** — this is a dialogue, not a form
4. **Explain the scores** — don't just dump numbers, interpret what they mean for the user
5. **Offer actionable advice** — which tasks to upskill in, what's safe, what to watch

### Programmatic API (for scripting, not chat)
```python
import sys; sys.path.insert(0, "scripts")
from profiler.occupation_search import load_occupations, search_occupations
from profiler.questionnaire import get_tasks_for_occupation, build_profile, calculate_personalised_score
from profiler.report import generate_markdown, generate_html

occs = load_occupations()
matches = search_occupations(occs, "registered nurse")
tasks = get_tasks_for_occupation(matches[0]["anzsco_code"])
selections = {t["id"]: {"does_task": True, "time_pct": 100/len(tasks)} for t in tasks}
profile = build_profile(matches[0]["anzsco_code"], selections)
profile["score"] = calculate_personalised_score(profile)
print(generate_markdown(profile))
```

### Optional LLM Enrichment
The profiler can call any OpenAI-compatible endpoint (Ollama, llama.cpp, LM Studio) to:
- Suggest custom tasks not in the standard list
- Infer workplace context from task selections
- Adjust automation scores based on the user's specific situation

```python
from profiler.enrichment import enrich_profile, is_llm_available
if is_llm_available("http://localhost:11434/v1"):
    profile = enrich_profile(profile, "http://localhost:11434/v1", model="llama3.2")
```

No API key needed for local models. No data leaves the machine.
