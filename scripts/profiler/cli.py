"""Interactive CLI for TaskFolio personal risk profiler."""
from __future__ import annotations

from pathlib import Path
from .occupation_search import load_occupations, search_occupations
from .questionnaire import get_tasks_for_occupation, build_profile, calculate_personalised_score
from .enrichment import is_llm_available, enrich_profile
from .report import generate_markdown, generate_html


def run():
    """Main interactive flow."""
    print("\n🎯 TaskFolio Personal Risk Profiler")
    print("=" * 40)

    # Step 1: Find occupation
    occupations = load_occupations()
    print(f"\n📊 {len(occupations)} occupations loaded.\n")

    query = input("What's your job title? > ").strip()
    if not query:
        print("No input. Exiting.")
        return

    matches = search_occupations(occupations, query)
    if not matches:
        print("No matching occupations found. Try a different title.")
        return

    print("\nMatches:")
    for i, m in enumerate(matches, 1):
        print(f"  {i}. {m['occupation_title']} (ANZSCO {m['anzsco_code']})")

    choice = input(f"\nSelect [1-{len(matches)}]: ").strip()
    try:
        selected_occ = matches[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    anzsco = selected_occ["anzsco_code"]

    # Step 2: Task questionnaire
    tasks = get_tasks_for_occupation(anzsco)
    print(f"\n📋 {selected_occ['occupation_title']} has {len(tasks)} tasks.\n")

    print("Which of these tasks do you perform? (y/n/s to skip rest)\n")

    selections = {}
    selected_tasks = []
    for i, task in enumerate(tasks, 1):
        ans = input(f"  {i}/{len(tasks)}: {task['description']}\n         [y/n/s] > ").strip().lower()
        if ans == "s":
            break
        if ans == "y":
            selected_tasks.append(task)
            selections[task["id"]] = {"does_task": True, "time_pct": 0}

    if not selected_tasks:
        print("No tasks selected. Exiting.")
        return

    # Time allocation
    print(f"\n⏱️  Allocate your time across {len(selected_tasks)} selected tasks (must total 100%):\n")
    remaining = 100
    for i, task in enumerate(selected_tasks):
        desc_short = task["description"][:60]
        if i == len(selected_tasks) - 1:
            pct = remaining
            print(f"  {desc_short}... → {pct}% (remainder)")
        else:
            pct_input = input(f"  {desc_short}...\n  Time % (remaining {remaining}%): > ").strip()
            try:
                pct = min(int(pct_input), remaining)
            except ValueError:
                pct = remaining // (len(selected_tasks) - i)
        selections[task["id"]]["time_pct"] = pct
        remaining -= pct

    # Step 3: Build profile + score
    profile = build_profile(anzsco, selections)
    profile["score"] = calculate_personalised_score(profile)

    # Step 4: Optional LLM enrichment
    enrich = input("\n🤖 Enrich with local LLM? (requires Ollama or compatible) [y/N] > ").strip().lower()
    if enrich == "y":
        llm_endpoint = input("  Endpoint [http://localhost:11434/v1]: > ").strip()
        if not llm_endpoint:
            llm_endpoint = "http://localhost:11434/v1"
        model = input("  Model [llama3.2]: > ").strip() or "llama3.2"
        if is_llm_available(llm_endpoint):
            print("  Enriching...")
            profile = enrich_profile(profile, llm_endpoint, model)
            if "enrichment_error" in profile:
                print(f"  ⚠️  Enrichment failed: {profile['enrichment_error']}")
            else:
                print("  ✅ Enriched!")
        else:
            print(f"  ⚠️  Endpoint not reachable: {llm_endpoint}")

    # Step 5: Generate reports
    md = generate_markdown(profile)
    print("\n" + md)

    save = input("\n💾 Save reports? [Y/n] > ").strip().lower()
    if save != "n":
        out_dir = Path("reports")
        out_dir.mkdir(exist_ok=True)
        slug = selected_occ["occupation_title"].lower().replace(" ", "-").replace("/", "-")

        md_path = out_dir / f"{slug}-report.md"
        md_path.write_text(md)
        print(f"  📄 {md_path}")

        html = generate_html(profile)
        html_path = out_dir / f"{slug}-report.html"
        html_path.write_text(html)
        print(f"  🌐 {html_path}")

    print("\nDone! 🎯")
