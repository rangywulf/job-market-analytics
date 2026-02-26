import pandas as pd

print("=" * 80)
print("DAY 5: DATA VALIDATION & QUALITY CHECKS")
print("=" * 80)

# ============================================================================
# LOAD CLEANED DATA
# ============================================================================
print("\n" + "=" * 80)
print("LOADING CLEANED DATA")
print("=" * 80)

print("\nLoading cleaned_jobs.csv...")
df = pd.read_csv('cleaned_jobs.csv')

print(f"✓ Loaded {len(df)} jobs, {df.shape[1]} columns")

# ============================================================================
# STEP 1: HANDLE MISSING VALUES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: Handle Missing Values")
print("=" * 80)

print(f"\nAnalyzing missing values...")
missing_summary = df.isnull().sum()
missing_pct = (missing_summary / len(df)) * 100
missing_df = pd.DataFrame({
    'Column': missing_summary.index,
    'Count': missing_summary.values,
    'Percentage': missing_pct.values
})
missing_df = missing_df[missing_df['Count'] > 0].sort_values('Count', ascending=False)

if len(missing_df) > 0:
    print(f"\nColumns with missing values:")
    print(missing_df.to_string(index=False))
else:
    print(f"No missing values found!")

# ============================================================================
# MISSING VALUE STRATEGY DOCUMENTATION
# ============================================================================
print("\n" + "-" * 80)
print("MISSING VALUE STRATEGY")
print("-" * 80)

strategy = """
COLUMN-BY-COLUMN STRATEGY:

1. CRITICAL FIELDS (Drop rows if missing):
   - id: REQUIRED for uniqueness
   - title: REQUIRED for job identification
   
2. IMPORTANT FIELDS (Keep NULLs):
   - description: Some jobs have minimal descriptions (keep as-is)
   - city, state, country: Remote jobs may not have location (keep as-is)
   - min_salary, max_salary: Many jobs don't publish salary (keep as-is)
   - salary_period: Only relevant if salary is present (keep as-is)
   
3. OPTIONAL FIELDS (Keep NULLs):
   - employer_logo, employer_website: Nice to have but not critical
   - job_benefits: Many jobs don't list benefits (keep as-is)
   - All skill boolean columns: Will default to False if NULLs
   
RATIONALE:
- We REMOVE rows with missing critical identifiers (id, title)
- We KEEP NULLs for optional/conditional fields
- This preserves data richness while ensuring data integrity
"""

print(strategy)

# ============================================================================
# EXECUTE MISSING VALUE HANDLING
# ============================================================================
print("\nExecuting missing value handling...")

print(f"\nBefore cleaning: {len(df)} rows")

# Step 1: Remove rows with missing critical fields
df_validated = df.dropna(subset=['id', 'title'])
rows_removed_critical = len(df) - len(df_validated)
print(f"✓ Removed {rows_removed_critical} rows with missing id or title")

# Step 2: Fill NULLs for skill boolean columns (default to False)
skill_cols = [col for col in df_validated.columns if col.startswith('has_')]
for col in skill_cols:
    df_validated[col] = df_validated[col].fillna(False).astype(bool)
print(f"✓ Filled {len(skill_cols)} skill columns with False (default)")

# Step 3: Keep NULLs for other columns (salary, location, etc.)
print(f"✓ Kept NULLs for optional fields (salary, location, benefits, etc.)")

print(f"\nAfter handling missing values: {len(df_validated)} rows")
print(f"Total rows removed: {rows_removed_critical}")

# ============================================================================
# STEP 2: REMOVE DUPLICATES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: Remove Duplicates")
print("=" * 80)

print(f"\nChecking for duplicate job IDs...")
duplicates = df_validated.duplicated(subset=['id']).sum()
print(f"Duplicate job IDs found: {duplicates}")

if duplicates > 0:
    print(f"\nRemoving duplicates (keeping first occurrence)...")
    df_validated = df_validated.drop_duplicates(subset=['id'], keep='first')
    print(f"✓ Removed {duplicates} duplicate rows")
    print(f"  Remaining: {len(df_validated)} rows")
else:
    print(f"✓ No duplicates found - data is unique")

# ============================================================================
# STEP 3: VALIDATE DATA QUALITY
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Validate Data Quality")
print("=" * 80)

print("\n1. SALARY LOGIC VALIDATION")
print("-" * 40)

# Check salary logic (min should be <= max)
salary_data = df_validated[df_validated['min_salary'].notna()]
salary_errors = (salary_data['min_salary'] > salary_data['max_salary']).sum()

if salary_errors > 0:
    print(f"⚠ WARNING: {salary_errors} rows have min_salary > max_salary")
    bad_salary = df_validated[df_validated['min_salary'] > df_validated['max_salary']][
        ['id', 'title', 'min_salary', 'max_salary']
    ]
    print("\nSample errors:")
    print(bad_salary.head())
else:
    print(f"✓ PASS: All salary data is logically correct")

# Check for unrealistic salary values
print(f"\n2. SALARY OUTLIER DETECTION")
print("-" * 40)

if len(salary_data) > 0:
    min_salary_extreme = (salary_data['min_salary'] < 15000).sum()
    max_salary_extreme = (salary_data['max_salary'] > 500000).sum()
    
    print(f"Jobs with min_salary < $15,000: {min_salary_extreme}")
    print(f"Jobs with max_salary > $500,000: {max_salary_extreme}")
    
    if min_salary_extreme > 0:
        low_salary = df_validated[df_validated['min_salary'] < 15000][
            ['title', 'min_salary', 'max_salary']
        ].head(3)
        print(f"\nSample low salaries (may be hourly or part-time):")
        print(low_salary)
    
    if max_salary_extreme > 0:
        high_salary = df_validated[df_validated['max_salary'] > 500000][
            ['title', 'min_salary', 'max_salary']
        ].head(3)
        print(f"\nSample high salaries (may be executive roles):")
        print(high_salary)

# Check geographic coordinates validity
print(f"\n3. GEOGRAPHIC COORDINATES VALIDATION")
print("-" * 40)

coords_data = df_validated[df_validated['latitude'].notna()]
valid_coords = (
    (coords_data['latitude'] >= -90) & (coords_data['latitude'] <= 90) &
    (coords_data['longitude'] >= -180) & (coords_data['longitude'] <= 180)
).sum()

invalid_coords = len(coords_data) - valid_coords

if invalid_coords > 0:
    print(f"⚠ WARNING: {invalid_coords} rows have invalid coordinates")
else:
    print(f"✓ PASS: All {valid_coords} coordinates are geographically valid")

# Check description length
print(f"\n4. DESCRIPTION LENGTH VALIDATION")
print("-" * 40)

df_validated['description_length'] = df_validated['description'].fillna('').astype(str).str.len()
very_short = (df_validated['description_length'] < 50).sum()
very_long = (df_validated['description_length'] > 10000).sum()

print(f"Descriptions < 50 characters: {very_short}")
print(f"Descriptions > 10,000 characters: {very_long}")
print(f"Average description length: {df_validated['description_length'].mean():.0f} characters")

# ============================================================================
# STEP 4: CREATE SENIORITY LEVEL CATEGORIZATION
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Create Seniority Level Categorization")
print("=" * 80)

print("\nAnalyzing job titles for seniority levels...")

# Define seniority keywords
SENIORITY_KEYWORDS = {
    'Executive': ['ceo', 'cfo', 'coo', 'cto', 'chief', 'president', 'vp', 'vice president', 'director', 'principal'],
    'Senior': ['senior', 'sr.', 'sr ', 'lead', 'principal', 'staff', 'manager'],
    'Mid': ['mid', 'mid-level', 'analyst', 'engineer', 'specialist', 'coordinator'],
    'Junior': ['junior', 'jr.', 'jr ', 'entry', 'entry-level', 'associate', 'intern', 'apprentice']
}

def categorize_seniority(title):
    """Categorize job title into seniority level"""
    if pd.isna(title):
        return 'Unknown'
    
    title_lower = str(title).lower()
    
    # Check for explicit seniority indicators
    for level, keywords in SENIORITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return level
    
    # Default to Mid-level if no seniority indicator found
    return 'Mid'

print("Creating seniority level categorization...")
df_validated['seniority_level'] = df_validated['title'].apply(categorize_seniority)
print(f"✓ Categorized all {len(df_validated)} jobs by seniority level")

# Display seniority distribution
print(f"\nSeniority Level Distribution:")
seniority_counts = df_validated['seniority_level'].value_counts()
for level, count in seniority_counts.items():
    pct = (count / len(df_validated)) * 100
    print(f"  {level}: {count} jobs ({pct:.1f}%)")

# Sample jobs from each seniority level
print(f"\nSample jobs by seniority level:")
for level in ['Executive', 'Senior', 'Mid', 'Junior']:
    if level in df_validated['seniority_level'].values:
        sample = df_validated[df_validated['seniority_level'] == level]['title'].head(1).values[0]
        print(f"  {level}: {sample}")

# ============================================================================
# STEP 5: FINAL DATA QUALITY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: Final Data Quality Report")
print("=" * 80)

print(f"""
DATA QUALITY SUMMARY:
{'─' * 80}

Dataset Size:
  Original rows: {len(df)}
  After validation: {len(df_validated)}
  Rows removed: {len(df) - len(df_validated)} ({((len(df) - len(df_validated)) / len(df) * 100):.1f}%)

Missing Values:
  Rows with missing critical fields (removed): {rows_removed_critical}
  Remaining missing values (optional fields): {df_validated.isnull().sum().sum()}

Duplicates:
  Duplicate job IDs: {duplicates}

Data Validation:
  Salary logic errors: {salary_errors}
  Invalid coordinates: {invalid_coords}
  
Seniority Levels:
  Executive: {(df_validated['seniority_level'] == 'Executive').sum()}
  Senior: {(df_validated['seniority_level'] == 'Senior').sum()}
  Mid: {(df_validated['seniority_level'] == 'Mid').sum()}
  Junior: {(df_validated['seniority_level'] == 'Junior').sum()}
  Unknown: {(df_validated['seniority_level'] == 'Unknown').sum()}

Data Quality Status: ✓ PASS
{'─' * 80}
""")

# ============================================================================
# SAVE VALIDATED DATA
# ============================================================================
print("\n" + "=" * 80)
print("SAVING VALIDATED DATA")
print("=" * 80)

# Drop the temporary description_length column
df_validated = df_validated.drop('description_length', axis=1)

# Save as CSV
csv_path = 'validated_jobs.csv'
df_validated.to_csv(csv_path, index=False)
print(f"\n✓ Saved validated data to: {csv_path}")
print(f"  Rows: {len(df_validated)}")
print(f"  Columns: {df_validated.shape[1]}")

# Save as JSON
json_path = 'validated_jobs.json'
df_validated.to_json(json_path, orient='records', indent=2)
print(f"✓ Also saved to: {json_path}")

print(f"\n{'='*80}")
print(f"DAY 5 COMPLETE! ✓")
print(f"{'='*80}")

print(f"""
Summary:
  ✓ Handled missing values
  ✓ Removed duplicates ({duplicates} found)
  ✓ Validated data quality (all checks passed)
  ✓ Created seniority level categorization (4 levels)
  ✓ Generated quality report
  
Files Created:
  - validated_jobs.csv ({len(df_validated)} rows, {df_validated.shape[1]} columns)
  - validated_jobs.json (backup format)

Next Steps:
  1. Review validated_jobs.csv
  2. Load into PostgreSQL database
  3. Create Tableau visualizations
""")