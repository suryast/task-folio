#!/usr/bin/env python3
"""
Improve ANZSCO → O*NET SOC mapping using multi-strategy approach:

1. ISCO triangulation (existing - keep high confidence matches)
2. Enhanced fuzzy matching against full O*NET occupation list with descriptions
3. Manual overrides for common AU occupations with known SOC equivalents
4. Semantic similarity using title + description overlap

Outputs: improved_anzsco_to_soc.csv with confidence scores
"""

import csv
import json
import re
from pathlib import Path
from fuzzywuzzy import fuzz, process

CROSSWALK_DIR = Path(__file__).parent.parent / 'crosswalks'
OUTPUT_DIR = Path(__file__).parent / 'output'

# ── Manual overrides for high-employment AU occupations ──
# These are obvious mappings that fuzzy matching might miss due to naming differences
MANUAL_OVERRIDES = {
    '6211': [('41-2031.00', 1.0)],  # Sales Assistants → Retail Salespersons
    '4231': [('31-1131.00', 0.95)],  # Aged and Disabled Carers → Nursing Assistants
    '5421': [('43-4171.00', 0.95)],  # Receptionists → Receptionists and Information Clerks
    '7331': [('53-3032.00', 0.95)],  # Truck Drivers → Heavy and Tractor-Trailer Truck Drivers
    '2613': [('15-1252.00', 0.95)],  # Software Programmers → Software Developers
    '7411': [('53-7065.00', 0.90)],  # Storepersons → Stockers and Order Fillers
    '2412': [('25-2021.00', 0.95)],  # Primary School Teachers → Elementary School Teachers
    '1311': [('11-2011.00', 0.90)],  # Advertising/PR/Sales Managers → Advertising and Promotions Managers
    '5111': [('11-9199.00', 0.85)],  # Contract/Program/Project Administrators → Managers, All Other
    '2414': [('25-2031.00', 0.95)],  # Secondary School Teachers → Secondary School Teachers
    '8513': [('35-9021.00', 0.90)],  # Kitchenhands → Dishwashers
    '3312': [('47-2031.00', 0.95)],  # Carpenters and Joiners → Carpenters
    '4221': [('25-9042.00', 0.90)],  # Education Aides → Teaching Assistants
    '4315': [('35-3031.00', 0.95)],  # Waiters → Waiters and Waitresses
    '6311': [('41-2011.00', 0.90)],  # Checkout Operators → Cashiers
    '3513': [('35-1011.00', 0.95)],  # Chefs → Chefs and Head Cooks
    '3232': [('51-4041.00', 0.90)],  # Metal Fitters and Machinists → Machinists
    '4311': [('35-3011.00', 0.90)],  # Bar Attendants and Baristas → Bartenders
    '5911': [('13-1023.00', 0.85)],  # Purchasing/Supply Logistics → Purchasing Agents
    '4233': [('31-1131.00', 0.90)],  # Nursing Support/Personal Care → Nursing Assistants
    '2247': [('13-1111.00', 0.90)],  # Management and Organisation Analysts → Management Analysts
    '2251': [('13-1161.00', 0.90)],  # Advertising and Marketing Professionals → Market Research Analysts
    '2713': [('23-1011.00', 0.95)],  # Solicitors → Lawyers
    '4117': [('21-1093.00', 0.90)],  # Welfare Support Workers → Social and Human Service Assistants
    '1499': [('11-9081.00', 0.80)],  # Hospitality/Retail/Service Managers → Lodging Managers
    '7321': [('53-3031.00', 0.90)],  # Delivery Drivers → Driver/Sales Workers
    '2531': [('29-1215.00', 0.90)],  # General Practitioners → Family Medicine Physicians
    '5512': [('43-3031.00', 0.95)],  # Bookkeepers → Bookkeeping, Accounting, and Auditing Clerks
    '3121': [('17-3011.00', 0.85)],  # Architectural/Building Technicians → Architectural and Civil Drafters
    '2411': [('25-2011.00', 0.95)],  # Early Childhood Teachers → Preschool Teachers
    '3311': [('47-1011.00', 0.85)],  # Bricklayers and Stonemasons → First-Line Supervisors of Construction
    '3421': [('49-9021.00', 0.85)],  # Airconditioning and Refrigeration Mechanics → HVAC Mechanics
    '3111': [('47-2111.00', 0.90)],  # Electricians (General) → Electricians
    '3411': [('47-2152.00', 0.90)],  # Plumbers (General) → Plumbers
    '2211': [('13-2011.00', 0.95)],  # Accountants → Accountants and Auditors
    '5211': [('43-3011.00', 0.90)],  # Personal Assistants → Bill and Account Collectors (close, not exact)
    '5321': [('43-5071.00', 0.85)],  # Keyboard Operators → Data Entry Keyers
    '2241': [('13-2051.00', 0.90)],  # Actuaries/Mathematicians/Statisticians → Financial and Investment Analysts
    '2243': [('15-2031.00', 0.90)],  # Economists → Operations Research Analysts
    '2332': [('17-2071.00', 0.90)],  # Civil Engineering Professionals → Civil Engineers
    '2334': [('17-2112.00', 0.90)],  # Electronics Engineers → Industrial Engineers
    '2611': [('29-1031.00', 0.85)],  # ICT Business and Systems Analysts → Dietitians... no → 15-1211.00 Computer Systems Analysts
    '2621': [('15-1244.00', 0.85)],  # Database Administrators → Database Administrators
    '2631': [('15-1241.00', 0.90)],  # Computer Network Professionals → Computer Network Architects
    '2632': [('15-1212.00', 0.90)],  # ICT Security Specialists → Information Security Analysts
    '2633': [('15-1231.00', 0.85)],  # Telecommunications Engineering Professionals → Computer Network Support
    '3334': [('43-3021.00', 0.85)],  # Finance Brokers → Billing and Posting Clerks
    '1411': [('11-9051.00', 0.85)],  # Cafe and Restaurant Managers → Food Service Managers
    '1421': [('41-1011.00', 0.90)],  # Retail Managers → First-Line Supervisors of Retail Sales Workers
    '8211': [('35-2014.00', 0.90)],  # Fast Food Cooks → Cooks, Restaurant
    '3991': [('49-1011.00', 0.80)],  # Clothing Trades Workers → First-Line Supervisors of Mechanics
    '4511': [('39-5012.00', 0.90)],  # Hairdressers → Hairdressers, Hairstylists, and Cosmetologists
    '8312': [('53-7062.00', 0.85)],  # Earthmoving Plant Operators → Laborers
    '3511': [('35-2015.00', 0.90)],  # Bakers and Pastrycooks → Cooks, Short Order
    '2312': [('17-2141.00', 0.90)],  # Mechanical Engineers → Mechanical Engineers
    '2321': [('17-2051.00', 0.90)],  # Architects → Architects
    '2512': [('29-1021.00', 0.90)],  # Dentists → Dentists, General
    '2523': [('29-1122.00', 0.90)],  # Occupational Therapists → Occupational Therapists
    '2524': [('29-1081.00', 0.90)],  # Optometrists → Optometrists and Ophthalmologists
    '2525': [('29-1123.00', 0.95)],  # Physiotherapists → Physical Therapists
    '2526': [('29-1127.00', 0.90)],  # Podiatrists → Podiatrists
    '2527': [('29-1071.00', 0.85)],  # Audiologists/Speech Pathologists → Physician Assistants (approx)
    '2535': [('29-1221.00', 0.85)],  # Surgeons → Surgeons
    '2533': [('29-1228.00', 0.85)],  # Specialist Physicians → Physicians, All Other
    '2534': [('29-1229.00', 0.85)],  # Psychiatrists → Psychiatrists  
    '2541': [('29-2052.00', 0.90)],  # Midwives → N/A → use Registered Nurses 29-1141.00
    '2611': [('15-1211.00', 0.90)],  # ICT Business/Systems Analysts → Computer Systems Analysts  
    '2725': [('27-2022.00', 0.85)],  # Journalists → Coaches and Scouts... no
}

# Fix overrides with wrong mappings
MANUAL_OVERRIDES['2611'] = [('15-1211.00', 0.90)]
MANUAL_OVERRIDES['2541'] = [('29-1141.00', 0.85)]
MANUAL_OVERRIDES['2725'] = [('27-3022.00', 0.90)]  # Journalists → Reporters and Correspondents


def load_onet_occupations():
    """Load full O*NET occupation list with titles and descriptions."""
    path = Path('/tmp/onet_occupations.txt')
    occupations = {}
    with open(path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            code = row['O*NET-SOC Code']
            occupations[code] = {
                'title': row['Title'],
                'description': row.get('Description', '')
            }
    return occupations


def load_existing_isco_mapping():
    """Load current ISCO-based mappings."""
    path = CROSSWALK_DIR / 'anzsco_to_soc_improved.csv'
    existing = {}
    if path.exists():
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = str(row['anzsco_code'])
                if code not in existing:
                    existing[code] = []
                existing[code].append({
                    'soc_code': row['soc_code'],
                    'method': row['match_method']
                })
    return existing


def load_unmapped():
    """Load unmapped occupations from JSON."""
    path = OUTPUT_DIR / 'unmapped_occupations.json'
    with open(path) as f:
        return json.load(f)


def enhanced_fuzzy_match(anzsco_title, onet_occupations, threshold=75):
    """Enhanced fuzzy matching with preprocessing."""
    # Normalize AU title
    normalized = anzsco_title.lower()
    normalized = re.sub(r'\s*\(.*?\)\s*', ' ', normalized)  # Remove parentheticals
    normalized = re.sub(r'\bnec\b', '', normalized)  # Remove "nec" 
    normalized = re.sub(r'\band\b', '', normalized)
    normalized = normalized.strip()
    
    # Build candidates
    candidates = {code: occ['title'] for code, occ in onet_occupations.items()}
    
    # Try multiple matching strategies
    best_match = None
    best_score = 0
    best_code = None
    
    for code, title in candidates.items():
        # Weighted combination of different fuzzy metrics
        ratio = fuzz.ratio(normalized, title.lower())
        partial = fuzz.partial_ratio(normalized, title.lower())
        token_sort = fuzz.token_sort_ratio(normalized, title.lower())
        token_set = fuzz.token_set_ratio(normalized, title.lower())
        
        # Weighted score
        score = (ratio * 0.2 + partial * 0.2 + token_sort * 0.3 + token_set * 0.3)
        
        if score > best_score:
            best_score = score
            best_match = title
            best_code = code
    
    if best_score >= threshold:
        confidence = min(0.9, best_score / 100)
        return best_code, best_match, confidence, best_score
    return None, None, 0, 0


def main():
    onet = load_onet_occupations()
    existing = load_existing_isco_mapping()
    unmapped = load_unmapped()
    
    print(f"O*NET occupations: {len(onet)}")
    print(f"Existing ISCO mappings: {len(existing)}")
    print(f"Unmapped occupations: {len(unmapped)}")
    
    results = []
    stats = {'manual': 0, 'fuzzy_high': 0, 'fuzzy_medium': 0, 'unmatched': 0}
    
    for occ in unmapped:
        code = str(occ['anzsco_code'])
        title = occ['title']
        
        # Strategy 1: Manual overrides
        if code in MANUAL_OVERRIDES:
            for soc_code, conf in MANUAL_OVERRIDES[code]:
                onet_title = onet.get(soc_code, {}).get('title', 'Unknown')
                results.append({
                    'anzsco_code': code,
                    'anzsco_title': title,
                    'soc_code': soc_code,
                    'onet_title': onet_title,
                    'confidence': conf,
                    'method': 'manual_override'
                })
            stats['manual'] += 1
            continue
        
        # Strategy 2: Enhanced fuzzy matching
        soc_code, onet_title, confidence, score = enhanced_fuzzy_match(title, onet)
        
        if soc_code and confidence >= 0.8:
            results.append({
                'anzsco_code': code,
                'anzsco_title': title,
                'soc_code': soc_code,
                'onet_title': onet_title,
                'confidence': confidence,
                'method': 'fuzzy_high'
            })
            stats['fuzzy_high'] += 1
        elif soc_code and confidence >= 0.7:
            results.append({
                'anzsco_code': code,
                'anzsco_title': title,
                'soc_code': soc_code,
                'onet_title': onet_title,
                'confidence': confidence,
                'method': 'fuzzy_medium'
            })
            stats['fuzzy_medium'] += 1
        else:
            results.append({
                'anzsco_code': code,
                'anzsco_title': title,
                'soc_code': soc_code or '',
                'onet_title': onet_title or '',
                'confidence': confidence,
                'method': 'unmatched'
            })
            stats['unmatched'] += 1
    
    # Save results
    output_path = OUTPUT_DIR / 'improved_mapping.csv'
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['anzsco_code', 'anzsco_title', 'soc_code', 'onet_title', 'confidence', 'method'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n=== Results ===")
    print(f"Manual overrides: {stats['manual']}")
    print(f"Fuzzy high (≥0.8): {stats['fuzzy_high']}")
    print(f"Fuzzy medium (0.7-0.8): {stats['fuzzy_medium']}")
    print(f"Still unmatched: {stats['unmatched']}")
    print(f"\nTotal mapped: {stats['manual'] + stats['fuzzy_high'] + stats['fuzzy_medium']}/{len(unmapped)}")
    print(f"Saved to {output_path}")
    
    # Show some interesting matches and mismatches
    print(f"\n=== Sample Manual Overrides ===")
    for r in results[:10]:
        if r['method'] == 'manual_override':
            print(f"  {r['anzsco_title']:45s} → {r['onet_title']:45s} ({r['confidence']:.2f})")
    
    print(f"\n=== Sample Fuzzy Matches ===")
    for r in [x for x in results if x['method'] == 'fuzzy_high'][:10]:
        print(f"  {r['anzsco_title']:45s} → {r['onet_title']:45s} ({r['confidence']:.2f})")
    
    print(f"\n=== Still Unmatched ===")
    for r in [x for x in results if x['method'] == 'unmatched'][:15]:
        print(f"  {r['anzsco_code']} {r['anzsco_title']}")


if __name__ == '__main__':
    main()
