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

TaskFolio includes a local personal risk profiler that agents can run for users.

### Data
- Master dataset: `public/data/pipeline/output/tasks_cache.json` (6,690 tasks across 361 occupations)
- Each task has: `id`, `description`, `automation_pct`, `augmentation_pct`, `timeframe`, `occupation_title`, `anzsco_code`
- Occupations use ANZSCO codes (Australian) with O*NET crosswalk

### Running the Profiler
```bash
cd scripts && python3 -m profiler
```

### Agent Workflow (non-interactive)
For coding agents that can't do interactive prompts, use the modules directly:

```python
from profiler.occupation_search import load_occupations, search_occupations
from profiler.questionnaire import get_tasks_for_occupation, build_profile, calculate_personalised_score
from profiler.enrichment import enrich_profile
from profiler.report import generate_markdown, generate_html

# 1. Find occupation
occs = load_occupations()
matches = search_occupations(occs, "registered nurse")

# 2. Get tasks + build profile
tasks = get_tasks_for_occupation(matches[0]["anzsco_code"])
selections = {t["id"]: {"does_task": True, "time_pct": 100/len(tasks)} for t in tasks}
profile = build_profile(matches[0]["anzsco_code"], selections)
profile["score"] = calculate_personalised_score(profile)

# 3. Optional: enrich with local LLM
# profile = enrich_profile(profile, endpoint="http://localhost:11434/v1")

# 4. Generate reports
print(generate_markdown(profile))
html = generate_html(profile)
```

### Enrichment
The profiler can optionally call any OpenAI-compatible endpoint (Ollama, llama.cpp, LM Studio) to:
- Suggest custom tasks not in the standard list
- Infer workplace context from task selections
- Adjust automation scores based on user's specific situation

No API key needed for local models. No data leaves the machine.
