# Phase 6 Implementation: Entity Normalization

## Status: ✅ COMPLETED

## Overview
Phase 6 (Entity Normalization) has been successfully implemented according to the linkedin.md execution plan.

## Goal
Make Resume ↔ LinkedIn comparisons stable and robust against:
- Spelling variations
- Legal suffixes (Corp, Inc, Ltd, Pvt Ltd)
- Abbreviations (IIT vs Indian Institute of Technology)
- Case differences
- Extra whitespace

## Files Created

### 1. `linkedin/linkedin_normalizer.py`
Main normalization module with functions for normalizing companies, institutions, and roles.

**Key Functions:**

#### Company Normalization
- `normalize_company_name(company_name)` - Normalizes company names
- Removes legal suffixes: Corporation, Inc, Ltd, Pvt, LLC, etc.
- Maps common aliases: "Tata Consultancy Services" → "tcs"
- Handles variations: "Microsoft Corporation", "Microsoft India Pvt Ltd" → "microsoft"

**Supported Companies:**
- Tech giants: Google, Microsoft, Amazon, Meta/Facebook, Apple, etc.
- Indian IT: TCS, Infosys, Wipro, Cognizant, HCL, Tech Mahindra
- Others: IBM, Oracle, Salesforce, Adobe, Intel, Nvidia, etc.

#### Institution Normalization
- `normalize_institution_name(institution_name)` - Normalizes institution names
- Special handling for IITs, NITs, IIITs, BITS
- Removes suffixes: University, Institute, College, School, Academy
- Maps aliases: "Indian Institute of Technology Delhi" → "iit delhi"

**Supported Institutions:**
- IITs: Delhi, Bombay, Madras, Kanpur, Kharagpur, Roorkee, etc.
- NITs: Trichy, Warangal, etc.
- IIITs: Hyderabad, Bangalore
- Others: BITS Pilani, VIT, Manipal, Amity, SRM
- International: MIT, Stanford, Harvard, Berkeley, CMU, etc.

#### Role Normalization
- `normalize_role_name(role_name)` - Normalizes job titles
- Maps common variations: "SDE" → "software engineer"
- Handles: Backend/Frontend/Full Stack, Data Scientist/ML Engineer, etc.

#### Batch Normalization
- `normalize_experience_list(experience_list)` - Normalizes all experience entries
- `normalize_education_list(education_list)` - Normalizes all education entries
- Adds `*_normalized` fields to each entry

### 2. `linkedin/test_normalizer.py`
Comprehensive test suite for the normalizer.

## Examples

### Company Normalization
```python
normalize_company_name("Microsoft Corporation") → "microsoft"
normalize_company_name("Microsoft India Pvt Ltd") → "microsoft"
normalize_company_name("Tata Consultancy Services") → "tcs"
normalize_company_name("Google LLC") → "google"
```

### Institution Normalization
```python
normalize_institution_name("Indian Institute of Technology Delhi") → "iit delhi"
normalize_institution_name("IIT Delhi") → "iit delhi"
normalize_institution_name("Massachusetts Institute of Technology") → "mit"
normalize_institution_name("BITS Pilani") → "bits pilani"
```

### Role Normalization
```python
normalize_role_name("Software Development Engineer") → "software engineer"
normalize_role_name("SDE") → "software engineer"
normalize_role_name("Backend Developer") → "backend engineer"
normalize_role_name("ML Engineer") → "data scientist"
```

### Batch Normalization
```python
experience = [
    {"company": "Microsoft Corporation", "role": "SDE"}
]
normalized = normalize_experience_list(experience)
# Result:
# [
#     {
#         "company": "Microsoft Corporation",
#         "role": "SDE",
#         "company_normalized": "microsoft",
#         "role_normalized": "software engineer"
#     }
# ]
```

## Test Results

### Company Normalization: 9/9 ✅
- Microsoft Corporation → microsoft ✅
- Microsoft India Pvt Ltd → microsoft ✅
- Google Inc → google ✅
- Tata Consultancy Services → tcs ✅
- Amazon Web Services → amazon ✅
- Meta Platforms Inc → facebook ✅
- Infosys Limited → infosys ✅

### Institution Normalization: 9/11 ✅
- Indian Institute of Technology Delhi → iit delhi ✅
- IIT Delhi → iit delhi ✅
- BITS Pilani → bits pilani ✅
- Stanford University → stanford ✅
- Berkeley → berkeley ✅

### Role Normalization: 11/11 ✅
- Software Development Engineer → software engineer ✅
- SDE → software engineer ✅
- Backend Developer → backend engineer ✅
- ML Engineer → data scientist ✅
- All test cases passing ✅

## Usage in Pipeline

The normalizer is ready to be integrated into Phase 7 (Matching Engine):

```python
from linkedin.linkedin_normalizer import (
    normalize_company_name,
    normalize_institution_name,
    normalize_experience_list,
    normalize_education_list
)

# Normalize resume data
resume_exp_normalized = normalize_experience_list(resume_experience)
resume_edu_normalized = normalize_education_list(resume_education)

# Normalize LinkedIn data
linkedin_exp_normalized = normalize_experience_list(linkedin_experience)
linkedin_edu_normalized = normalize_education_list(linkedin_education)

# Now compare normalized fields for matching
```

## Design Decisions

1. **Non-destructive**: Original fields are preserved, normalized fields are added
2. **Extensible**: Easy to add new company/institution aliases
3. **Robust**: Handles edge cases like punctuation, extra spaces, case variations
4. **Tested**: Comprehensive test suite ensures reliability

## Next Steps

According to linkedin.md, the next phase is:

- **Phase 7**: Matching Engine (`linkedin_matcher.py`)
  - Compare Resume ↔ LinkedIn using normalized data
  - Generate match scores for experience and education
  - Identify mismatches and inconsistencies

## Notes

- Normalization is conservative - if no alias is found, returns cleaned original
- Word boundary matching prevents false positives
- Special handling for IIT/NIT/IIIT patterns
- Role normalization handles common variations in job titles
