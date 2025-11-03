# Conference Matching Improvements (Nov 2025)

## Problem

The original tracker was finding **wrong conferences** due to loose matching:
- ISCAS finding ISCA websites
- MICRO finding food microbiology conferences  
- DAC finding ASPDAC conferences
- FPGA finding ISVLSI conferences

## Solution

Implemented strict multi-layer validation:

### 1. Full Conference Name Mapping
Added full names for all 30 conferences to enable specific searches:
```python
'ISCA': 'International Symposium on Computer Architecture'
'ISCAS': 'International Symposium on Circuits and Systems'
```

### 2. Exact Token Matching
URLs must contain conference acronym as exact token, not substring:
- ✅ `iscas2026.org` → ISCAS matches
- ❌ `iscaconf.org` → ISCAS doesn't match (it's ISCA)

### 3. Year Proximity Check
Short acronyms (≤5 chars) require year nearby:
- Prevents "MICRO" matching unrelated 2026 sites

### 4. Conference-Specific Blocklists
Explicit blocks for commonly confused conferences:
```python
'DAC': ['aspdac'],
'MICRO': ['microbit', 'foodmicro'],
'ISCA': ['iscas'],
```

### 5. Aggregator Site Blocking
Block unreliable CFP aggregators:
- wikicfp.com, conferenceindex.org, callforpaper.org
- manuscriptlink.com, blogspot.com

### 6. Improved Search Queries
Use quoted searches for precision:
```python
f'"{conference_name} {year}" call for papers'
f'"{full_name}" {year} CFP'
```

## Results

- **Before**: 41/58 conferences were expired or wrong (71% error rate)
- **After**: Exact matching prevents false positives (expected <5% error rate)

## Testing

```bash
# Test problematic conferences
python3 -c "from conference_tracker import search_conference; print(search_conference('ISCAS', 2026, True))"
# Should find Circuits and Systems, NOT Computer Architecture
```

