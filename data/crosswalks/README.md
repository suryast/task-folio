# ISCO-08 Triangulation Crosswalk

Improves ANZSCO → SOC matching from **41%** (fuzzy title) to **62.6%** (official crosswalks).

## Method

```
ANZSCO (AU) ──→ ISCO-08 (ILO) ──→ SOC (US/O*NET)
    │              │                │
    └──ABS─────────┴──BLS───────────┘
       concordance    crosswalk
```

## Files

| File | Description |
|------|-------------|
| `anzsco_isco08.xls` | ABS ANZSCO → ISCO-08 concordance (source) |
| `anzsco_to_isco08.csv` | Cleaned ANZSCO → ISCO-08 (1,272 mappings) |
| `soc_to_isco08.csv` | Manual SOC → ISCO-08 (453 mappings) |
| `anzsco_to_soc_via_isco.csv` | Triangulated 6-digit ANZSCO → SOC |
| `anzsco_to_soc_improved.csv` | 4-digit ANZSCO → SOC for TaskFolio (346 rows) |

## Coverage

| Metric | Old (Fuzzy) | New (ISCO) |
|--------|-------------|------------|
| ANZSCO matched | 147 | 92 |
| Match quality | ~75% avg | Official crosswalks |
| Still need LLM | 214 | 55 |

## Example Improvements

| ANZSCO | Title | Old SOC (fuzzy) | New SOC (ISCO) |
|--------|-------|-----------------|----------------|
| 5616 | Switchboard Operators | Motorboat Operators (70%) | Dispatchers |
| 8213 | Fencers | Dancers (71%) | Cement Masons/Fencers |
| 5321 | Keyboard Operators | Dredge Operators (71%) | Data Entry Keyers |
| 4521 | Fitness Instructors | Fire Inspectors (71%) | Fitness Trainers |

## Next Steps

1. **V1.1**: Use `anzsco_to_soc_improved.csv` as primary lookup
2. **Fallback**: Fuzzy match for unmatched occupations
3. **Final fallback**: LLM task generation

## Sources

- ABS: [ANZSCO-ISCO Correspondence](https://archive.org/details/12200-2013)
- BLS: [SOC-ISCO Crosswalk](https://www.bls.gov/soc/soccrosswalks.htm)
- Manual SOC→ISCO mapping from known equivalences

---
Generated: 2026-03-21
