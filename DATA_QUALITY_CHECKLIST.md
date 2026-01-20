# Data Quality Checklist
## Job Market Analytics Pipeline

---

## Quality Checks Before Database Loading

### ✅ Completeness Checks

- [ ] **job_id**: Verify all jobs have unique, non-null IDs
  - Expected: 100% populated
  - Current: 100%
  - Action: Reject records without job_id

- [ ] **job_title**: Check all jobs have titles
  - Expected: 100% populated
  - Current: 100%
  - Action: Reject records without titles

- [ ] **employer_name**: Verify company names exist
  - Expected: 100% populated
  - Current: 100%
  - Action: Reject records without company names

- [ ] **job_description**: Check descriptions are present
  - Expected: 100% populated
  - Current: 100%
  - Action: Reject if missing

- [ ] **job_location, job_city, job_state, job_country**: Location data
  - Expected: 100% populated
  - Current: 100%
  - Action: Reject if any location field missing

- [ ] **Salary fields**: Acknowledge they're sparse
  - Expected: ~45-55% populated
  - Current: 50% populated (10/20)
  - Action: Allow NULLs, filter in queries where needed

---

### ✅ Uniqueness Checks

- [ ] **No duplicate job_id**: Each job should appear only once
  - Check: `SELECT job_id, COUNT(*) FROM raw_jobs GROUP BY job_id HAVING COUNT(*) > 1`
  - Action: Remove duplicates, keep most recent

- [ ] **Company name uniqueness**: Same company names should refer to same entity
  - Check: Compare spelling variations (Jobs via Dice vs Dice)
  - Action: Standardize company names during cleaning

---

### ✅ Validity Checks

- [ ] **job_id format**: Should be non-empty string
  - Sample: `eFAJxWm6f98Rg1UGAAAAAA==`
  - Action: Reject if empty or malformed

- [ ] **job_is_remote**: Must be boolean (True/False)
  - Expected: Yes/No or 0/1 or True/False
  - Current: boolean
  - Action: Convert to TRUE/FALSE if needed

- [ ] **job_latitude/longitude**: Must be valid floats
  - Expected range: -90 to 90 (latitude), -180 to 180 (longitude)
  - Action: Validate ranges, reject if outside bounds

- [ ] **job_country**: Should be 2-letter country code
  - Sample: US, UK, CA, etc.
  - Current: "US"
  - Action: Validate against ISO 3166-1 alpha-2

- [ ] **job_employment_type**: Should be standard value
  - Valid: Full-time, Part-time, Contract, Temporary, Internship
  - Action: Standardize variations

- [ ] **job_salary_period**: Should be YEARLY, MONTHLY, or HOURLY
  - Current: "YEAR" (should be "YEARLY")
  - Action: Standardize to YEARLY/MONTHLY/HOURLY

- [ ] **Salary values**: job_min_salary <= job_max_salary
  - Action: Flag and investigate if min > max

---

### ✅ Consistency Checks

- [ ] **Location consistency**: If job_city is provided, job_state should be provided
  - Check: city without state
  - Action: Reject or fill with geocoding if possible

- [ ] **Salary consistency**: If one salary is provided, period should be provided
  - Check: salary without job_salary_period
  - Action: Infer period or reject

- [ ] **Posted date consistency**: job_posted_at_timestamp should match job_posted_at_datetime_utc
  - Check: Convert timestamp to datetime and compare
  - Action: Flag if mismatch > 1 day

- [ ] **URL validity**: job_apply_link and job_google_link should be valid URLs
  - Check: Starts with https://, not empty
  - Action: Flag invalid URLs but allow (they may still work)

---

### ✅ Outlier/Anomaly Checks

- [ ] **Salary outliers**: 
  - Check: job_min_salary < $20K or > $500K
  - Action: Flag for review but allow (senior/executive roles may justify)
  - Document: Note unusually high/low salaries

- [ ] **Job description length**: 
  - Check: Description < 100 characters or > 50,000 characters
  - Action: Flag short ones (may be errors), truncate extremely long ones

- [ ] **Skills extraction**: 
  - Check: How many qualifications/skills are extracted per job
  - Expected: 3-15 per job
  - Action: Flag jobs with 0 or > 20 skills

- [ ] **Location outliers**: 
  - Check: Jobs with unrealistic coordinates (latitude/longitude)
  - Action: Flag and review

---

### ✅ Temporal Checks

- [ ] **Posted date reasonableness**: 
  - Check: job_posted_at_timestamp is recent (within last 365 days)
  - Current: All from January 2026
  - Action: Flag very old posts (> 2 years old)

- [ ] **Data collection date**: 
  - Check: fetched_at is current
  - Action: Log collection timestamp for each batch

---

## Data Quality Report Template

```
Data Quality Report
==================
Date: [TODAY]
Records Analyzed: [COUNT]

COMPLETENESS
- Fields always present: 30/31 (96.8%)
- Fields sometimes missing: 1/31 (3.2%)
  * job_salary (50% missing)

UNIQUENESS
- Duplicate job_ids: [COUNT]
- Unique companies: [COUNT]
- Jobs per company (avg): [AVG]

VALIDITY
- Invalid country codes: [COUNT]
- Latitude/longitude out of range: [COUNT]
- Salary min > max: [COUNT]
- Invalid URLs: [COUNT]

CONSISTENCY
- Location mismatches: [COUNT]
- Posted date inconsistencies: [COUNT]

OUTLIERS
- Salary > $500K: [COUNT]
- Salary < $20K: [COUNT]
- Description < 100 chars: [COUNT]
- Description > 50K chars: [COUNT]

SUMMARY
- % Records Passed: [PCT]%
- Records to Review: [COUNT]
- Records to Reject: [COUNT]
- Ready for Loading: [COUNT]
```

---

## Implementation Checklist

- [ ] Create data validation script in Python
- [ ] Generate automated quality report
- [ ] Log all rejected records with reasons
- [ ] Create manual review list for ambiguous cases
- [ ] Archive raw data before cleaning
- [ ] Document all transformations applied
- [ ] Create test data subset for loading validation

---

## Notes

1. **Salary data is sparse**: Only 50% of jobs have salary information. This is normal for job aggregation APIs.

2. **Benefits extraction**: Benefits come as lists, may need parsing/standardization

3. **Skills extraction**: Will be done during data cleaning phase by parsing job descriptions and highlights

4. **Company name standardization**: "Jobs via Dice" may appear with variations—normalize during cleaning

5. **Soft validation**: Some fields (URLs, etc.) should be logged but not rejected—they may still be valid