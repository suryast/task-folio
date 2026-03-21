#!/usr/bin/env python3
"""
Step 1 V2: Build ANZSCO -> SOC mapping using ISCO triangulation + fuzzy fallback.

Priority:
1. ISCO triangulation (official crosswalks)
2. Fuzzy title matching (fallback)
3. Mark as unmapped (needs LLM generation)
"""

import pandas as pd
from pathlib import Path
from fuzzywuzzy import fuzz

# Paths
CROSSWALK_DIR = Path(__file__).parent.parent / 'crosswalks'
OUTPUT_DIR = Path(__file__).parent / 'output'

def load_isco_mapping():
    """Load ISCO-triangulated mappings."""
    path = CROSSWALK_DIR / 'anzsco_to_soc_improved.csv'
    if not path.exists():
        print(f"Warning: {path} not found, skipping ISCO mapping")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} ISCO-triangulated mappings for {df['anzsco_code'].nunique()} occupations")
    return df

def load_anthropic_data():
    """Load Anthropic Economic Index data with SOC codes."""
    # This would be your Anthropic data file
    # For now, we'll use the O*NET occupation list
    path = Path(__file__).parent.parent / 'anthropic' / 'economic_index.json'
    if path.exists():
        import json
        with open(path) as f:
            data = json.load(f)
        return data
    return {}

def load_taskfolio_occupations():
    """Load the 361 TaskFolio target occupations."""
    # Load from existing mapping or D1 export
    path = OUTPUT_DIR / 'anzsco_onet_mapping.csv'
    if path.exists():
        df = pd.read_csv(path)
        return df[['anzsco_code', 'anzsco_title']].drop_duplicates()
    
    # Fallback: generate from known codes
    return pd.DataFrame()

def fuzzy_match_title(anzsco_title, onet_titles, threshold=0.70):
    """Fuzzy match ANZSCO title to O*NET titles."""
    best_match = None
    best_score = 0
    
    for soc_code, onet_title in onet_titles.items():
        score = fuzz.token_sort_ratio(anzsco_title.lower(), onet_title.lower()) / 100
        if score > best_score:
            best_score = score
            best_match = soc_code
    
    if best_score >= threshold:
        return best_match, best_score
    return None, 0

def build_mapping():
    """Build the improved ANZSCO -> SOC mapping."""
    
    # Load ISCO-triangulated mappings
    isco_map = load_isco_mapping()
    
    # Load target occupations
    targets = load_taskfolio_occupations()
    print(f"Target occupations: {len(targets)}")
    
    # Build final mapping
    results = []
    
    for _, row in targets.iterrows():
        anzsco = str(row['anzsco_code'])
        title = row['anzsco_title']
        
        # Check ISCO mapping first
        isco_matches = isco_map[isco_map['anzsco_code'].astype(str) == anzsco]
        
        if len(isco_matches) > 0:
            # Use first ISCO match (they're all valid)
            soc = isco_matches.iloc[0]['soc_code']
            results.append({
                'anzsco_code': anzsco,
                'anzsco_title': title,
                'soc_code': soc,
                'match_method': 'isco_triangulation',
                'confidence': 0.95  # High confidence for official crosswalk
            })
        else:
            # Mark as needing fuzzy match or LLM generation
            results.append({
                'anzsco_code': anzsco,
                'anzsco_title': title,
                'soc_code': None,
                'match_method': 'unmapped',
                'confidence': 0.0
            })
    
    df = pd.DataFrame(results)
    
    # Stats
    isco_matched = len(df[df['match_method'] == 'isco_triangulation'])
    unmapped = len(df[df['match_method'] == 'unmapped'])
    
    print(f"\nMapping results:")
    print(f"  ISCO triangulated: {isco_matched} ({100*isco_matched/len(df):.1f}%)")
    print(f"  Unmapped (need LLM): {unmapped} ({100*unmapped/len(df):.1f}%)")
    
    # Save
    output_path = OUTPUT_DIR / 'anzsco_soc_mapping_v2.csv'
    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")
    
    return df

if __name__ == '__main__':
    build_mapping()
