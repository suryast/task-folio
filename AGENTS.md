# Agent Instructions

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

## Issue Tracking

Use GitHub Issues for bug reports and feature requests.

## Session Completion

When ending a work session:

1. **Run quality gates** (if code changed) — tests, linters, builds
2. **Commit and push**:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
3. **Verify** — all changes committed AND pushed

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
