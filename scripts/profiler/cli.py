"""Interactive CLI for TaskFolio personal risk profiler."""
from __future__ import annotations

import shutil
from pathlib import Path
from .occupation_search import load_occupations, search_occupations
from .questionnaire import get_tasks_for_occupation, build_profile, calculate_personalised_score
from .enrichment import is_llm_available, enrich_profile
from .report import generate_markdown, generate_html

# Terminal colours (ANSI)
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"


def _width() -> int:
    return min(shutil.get_terminal_size().columns, 80)


def _box(text: str, emoji: str = "", colour: str = CYAN) -> str:
    w = _width()
    lines = text.split("\n")
    top = f"{colour}{'━' * w}{RESET}"
    bot = f"{colour}{'━' * w}{RESET}"
    body = "\n".join(f"  {line}" for line in lines)
    prefix = f"  {emoji}  " if emoji else "  "
    return f"\n{top}\n{prefix}{BOLD}{lines[0]}{RESET}\n{''.join(f'  {l}{chr(10)}' for l in lines[1:]) if len(lines) > 1 else ''}{bot}"


def _bar(value: float, width: int = 30, fill: str = "█", empty: str = "░") -> str:
    filled = int(value * width)
    return f"{fill * filled}{empty * (width - filled)}"


def _risk_colour(value: float) -> str:
    if value >= 0.7:
        return RED
    elif value >= 0.4:
        return YELLOW
    return GREEN


def _risk_label(value: float) -> str:
    if value >= 0.7:
        return "🔴 HIGH"
    elif value >= 0.4:
        return "🟡 MEDIUM"
    return "🟢 LOW"


def _separator(char: str = "─", colour: str = DIM) -> str:
    return f"{colour}{char * _width()}{RESET}"


def _print_score_card(profile: dict) -> None:
    """Print a rich terminal score card."""
    score = profile.get("score", {})
    overall = score.get("overall_exposure", 0)
    auto = score.get("automation_weighted", 0)
    aug = score.get("augmentation_weighted", 0)
    timeframes = score.get("timeframe_breakdown", {})

    w = _width()
    title = profile["occupation_title"]

    # Header
    print(f"\n{BOLD}{BG_BLACK}{WHITE}{'━' * w}{RESET}")
    print(f"{BOLD}{BG_BLACK}{WHITE}  🎯  YOUR PERSONAL AI EXPOSURE REPORT{' ' * (w - 40)}{RESET}")
    print(f"{BOLD}{BG_BLACK}{WHITE}{'━' * w}{RESET}")

    print(f"\n  {BOLD}{title}{RESET}  {DIM}(ANZSCO {profile['anzsco_code']}){RESET}")
    print(f"  {DIM}Analyzing {profile['tasks_selected']} of {profile['total_tasks_available']} tasks{RESET}")
    print()

    # Score cards
    print(_separator("─"))
    print(f"  {BOLD}📊 EXPOSURE SCORES{RESET}")
    print(_separator("─"))
    print()

    rc = _risk_colour(overall)
    print(f"  Overall Exposure    {rc}{_bar(overall)}{RESET}  {BOLD}{overall:.0%}{RESET}  {_risk_label(overall)}")
    rc = _risk_colour(auto)
    print(f"  🤖 Automation Risk  {rc}{_bar(auto)}{RESET}  {BOLD}{auto:.0%}{RESET}")
    rc = _risk_colour(aug)
    print(f"  🧠 Augmentation     {rc}{_bar(aug)}{RESET}  {BOLD}{aug:.0%}{RESET}")
    print()

    # Timeframe breakdown
    if timeframes:
        print(_separator("─"))
        print(f"  {BOLD}⏳ WHEN WILL AI AFFECT YOUR WORK?{RESET}")
        print(_separator("─"))
        print()

        tf_labels = {
            "now": ("⚡", "Happening now"),
            "1-2y": ("📅", "1-2 years"),
            "3-5y": ("🔮", "3-5 years"),
            "5-10y": ("🌅", "5-10 years"),
            "10y+": ("🏔️ ", "10+ years"),
        }

        for tf_key in ["now", "1-2y", "3-5y", "5-10y", "10y+"]:
            if tf_key in timeframes:
                emoji, label = tf_labels[tf_key]
                pct = timeframes[tf_key]
                bar_val = pct / 100
                colour = RED if tf_key == "now" else YELLOW if tf_key in ("1-2y", "3-5y") else GREEN
                print(f"  {emoji} {label:<16} {colour}{_bar(bar_val, 25)}{RESET}  {pct:.0f}%")

        print()

    # Task details
    print(_separator("─"))
    print(f"  {BOLD}📋 TASK BREAKDOWN{RESET}")
    print(_separator("─"))
    print()

    tasks = profile["selected_tasks"]
    for i, task in enumerate(tasks, 1):
        desc = task["description"]
        auto_pct = task["automation_pct"]
        aug_pct = task["augmentation_pct"]
        time_pct = task["time_pct"]
        tf = task.get("timeframe", "?")

        # Risk indicator
        total_risk = auto_pct + aug_pct
        if total_risk >= 0.7:
            indicator = f"{RED}▲{RESET}"
        elif total_risk >= 0.4:
            indicator = f"{YELLOW}▬{RESET}"
        else:
            indicator = f"{GREEN}▼{RESET}"

        tf_emoji = {"now": "⚡", "1-2y": "📅", "3-5y": "🔮", "5-10y": "🌅", "10y+": "🏔️ "}.get(tf, "❓")

        print(f"  {indicator} {BOLD}{desc}{RESET}")
        print(f"    {DIM}Time: {time_pct}% │ Auto: {auto_pct:.0%} │ Aug: {aug_pct:.0%} │ {tf_emoji} {tf}{RESET}")
        if i < len(tasks):
            print()

    print()

    # Enrichment
    if "enrichment" in profile:
        enrichment = profile["enrichment"]
        print(_separator("─"))
        print(f"  {BOLD}🤖 AI-ENHANCED INSIGHTS{RESET}")
        print(_separator("─"))
        print()

        if "workplace_context" in enrichment:
            print(f"  {MAGENTA}💼 Workplace:{RESET} {enrichment['workplace_context']}")
            print()

        if "custom_tasks" in enrichment and enrichment["custom_tasks"]:
            print(f"  {MAGENTA}✨ You might also do:{RESET}")
            for ct in enrichment["custom_tasks"]:
                print(f"     • {ct}")
            print()

    # Footer
    print(f"{BOLD}{BG_BLACK}{WHITE}{'━' * w}{RESET}")
    print(f"{BOLD}{BG_BLACK}{WHITE}  Generated by TaskFolio Personal Risk Profiler{' ' * (w - 49)}{RESET}")
    print(f"{BOLD}{BG_BLACK}{WHITE}{'━' * w}{RESET}")
    print()


def run():
    """Main interactive flow."""
    w = _width()

    # Banner
    print()
    print(f"{BOLD}{CYAN}{'━' * w}{RESET}")
    print(f"{BOLD}{CYAN}  🎯  TaskFolio — Personal Risk Profiler{RESET}")
    print(f"{BOLD}{CYAN}  {DIM}How will AI change YOUR job?{RESET}")
    print(f"{BOLD}{CYAN}{'━' * w}{RESET}")

    # Step 1: Find occupation
    occupations = load_occupations()
    print(f"\n  {DIM}📊 {len(occupations)} Australian occupations loaded{RESET}\n")

    query = input(f"  {BOLD}What's your job title?{RESET} › ").strip()
    if not query:
        print(f"\n  {RED}No input. Exiting.{RESET}")
        return

    matches = search_occupations(occupations, query)
    if not matches:
        print(f"\n  {RED}❌ No matching occupations found. Try a different title.{RESET}")
        return

    print(f"\n  {BOLD}Found {len(matches)} match{'es' if len(matches) > 1 else ''}:{RESET}\n")
    for i, m in enumerate(matches, 1):
        print(f"    {CYAN}{BOLD}{i}{RESET}  {m['occupation_title']}  {DIM}ANZSCO {m['anzsco_code']}{RESET}")

    print()
    choice = input(f"  {BOLD}Select{RESET} [{CYAN}1-{len(matches)}{RESET}] › ").strip()
    try:
        selected_occ = matches[int(choice) - 1]
    except (ValueError, IndexError):
        print(f"\n  {RED}Invalid selection.{RESET}")
        return

    anzsco = selected_occ["anzsco_code"]
    occ_title = selected_occ["occupation_title"]

    # Step 2: Task questionnaire
    tasks = get_tasks_for_occupation(anzsco)

    print(f"\n{_separator('─')}")
    print(f"  {BOLD}📋 Task Selection — {occ_title}{RESET}")
    print(f"  {DIM}{len(tasks)} tasks to review{RESET}")
    print(_separator("─"))
    print(f"\n  {DIM}For each task: {GREEN}y{RESET}{DIM}=yes I do this  {RED}n{RESET}{DIM}=no  {YELLOW}s{RESET}{DIM}=skip remaining{RESET}\n")

    selections = {}
    selected_tasks = []
    for i, task in enumerate(tasks, 1):
        counter = f"{DIM}[{i}/{len(tasks)}]{RESET}"
        print(f"  {counter} {task['description']}")
        ans = input(f"         {BOLD}›{RESET} ").strip().lower()
        if ans == "s":
            print(f"\n  {YELLOW}⏭️  Skipped remaining tasks{RESET}")
            break
        if ans == "y":
            selected_tasks.append(task)
            selections[task["id"]] = {"does_task": True, "time_pct": 0}
            print(f"         {GREEN}✓ Added{RESET}")
        else:
            print(f"         {DIM}– Skipped{RESET}")

    if not selected_tasks:
        print(f"\n  {RED}❌ No tasks selected. Exiting.{RESET}")
        return

    # Time allocation
    print(f"\n{_separator('─')}")
    print(f"  {BOLD}⏱️  Time Allocation{RESET}")
    print(f"  {DIM}How do you split your time? (must total 100%){RESET}")
    print(_separator("─"))
    print()

    remaining = 100
    for i, task in enumerate(selected_tasks):
        desc_short = task["description"][:55]
        if len(task["description"]) > 55:
            desc_short += "…"

        if i == len(selected_tasks) - 1:
            pct = remaining
            print(f"  {BOLD}{desc_short}{RESET}")
            print(f"    → {GREEN}{pct}%{RESET} {DIM}(remainder){RESET}")
        else:
            print(f"  {BOLD}{desc_short}{RESET}")
            pct_input = input(f"    {DIM}Remaining: {remaining}%{RESET}  › ").strip()
            try:
                pct = max(0, min(int(pct_input), remaining))
            except ValueError:
                pct = remaining // (len(selected_tasks) - i)
                print(f"    {YELLOW}→ Auto-assigned {pct}%{RESET}")

        selections[task["id"]]["time_pct"] = pct
        remaining -= pct
        print()

    # Step 3: Build profile + score
    print(f"  {DIM}⏳ Calculating your personalised score...{RESET}")
    profile = build_profile(anzsco, selections)
    profile["score"] = calculate_personalised_score(profile)

    # Step 4: Optional LLM enrichment
    print()
    enrich = input(f"  {BOLD}🤖 Enrich with local LLM?{RESET} {DIM}(Ollama/compatible){RESET} [{CYAN}y/N{RESET}] › ").strip().lower()
    if enrich == "y":
        llm_endpoint = input(f"    Endpoint {DIM}[http://localhost:11434/v1]{RESET} › ").strip()
        if not llm_endpoint:
            llm_endpoint = "http://localhost:11434/v1"
        model = input(f"    Model {DIM}[llama3.2]{RESET} › ").strip() or "llama3.2"
        if is_llm_available(llm_endpoint):
            print(f"    {DIM}⏳ Enriching with {model}...{RESET}")
            profile = enrich_profile(profile, llm_endpoint, model)
            if "enrichment_error" in profile:
                print(f"    {RED}⚠️  Enrichment failed: {profile['enrichment_error']}{RESET}")
            else:
                print(f"    {GREEN}✅ Enriched!{RESET}")
        else:
            print(f"    {RED}⚠️  Endpoint not reachable: {llm_endpoint}{RESET}")

    # Step 5: Display rich terminal report
    _print_score_card(profile)

    # Step 6: Save reports
    save = input(f"  {BOLD}💾 Save reports?{RESET} [{CYAN}Y/n{RESET}] › ").strip().lower()
    if save != "n":
        out_dir = Path("reports")
        out_dir.mkdir(exist_ok=True)
        slug = occ_title.lower().replace(" ", "-").replace("/", "-")

        md = generate_markdown(profile)
        md_path = out_dir / f"{slug}-report.md"
        md_path.write_text(md)
        print(f"    {GREEN}📄 {md_path}{RESET}")

        html = generate_html(profile)
        html_path = out_dir / f"{slug}-report.html"
        html_path.write_text(html)
        print(f"    {GREEN}🌐 {html_path}{RESET}")

    print(f"\n  {BOLD}🎯 Done! Go build your future.{RESET}\n")
