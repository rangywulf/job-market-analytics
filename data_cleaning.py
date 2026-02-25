import json
import pandas as pd
import re
from datetime import datetime
from collections import Counter

print("="*80)
print("DATA CLEANING & STANDARDIZATION")
print("="*80)

# ============================================================================
# STEP 1: PARSE JOB DATA AND STANDARDIZE FIELD NAMES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: Parse Job Data & Standardize Field Names")
print("=" * 80)

# Load raw job data
print("\nLoading raw_jobs.json...")
with open('raw_jobs.json', 'r', encoding='utf-8') as f:
    raw_jobs = json.load(f)

df = pd.DataFrame(raw_jobs)
print(f"✓ Loaded {len(df)} jobs, {df.shape[1]} columns")

# Standardize field names - remove "job_" prefix for cleaner naming
print("\nStandardizing field names...")
rename_mapping = {
    'job_id': 'id',
    'job_title': 'title',
    'job_description': 'description',
    'job_location': 'location',
    'job_city': 'city',
    'job_state': 'state',
    'job_country': 'country',
    'job_latitude': 'latitude',
    'job_longitude': 'longitude',
    'job_is_remote': 'is_remote',
    'job_employment_type': 'employment_type',
    'job_publisher': 'publisher',
    'job_apply_link': 'apply_link',
    'job_apply_is_direct': 'apply_is_direct',
    'job_google_link': 'google_link',
    'job_min_salary': 'min_salary',
    'job_max_salary': 'max_salary',
    'job_salary_period': 'salary_period',
    'job_onet_soc': 'onet_soc',
    'job_onet_job_zone': 'onet_job_zone',
    'job_posted_at': 'posted_at_relative',
    'job_posted_at_datetime_utc': 'posted_at',
    'job_posted_at_timestamp': 'posted_at_timestamp',
}

df = df.rename(columns=rename_mapping)
print(f"✓ Renamed {len(rename_mapping)} columns")
print(f"✓ New column count: {df.shape[1]}")

# ============================================================================
# STEP 2: EXTRACT & NORMALIZE SALARY INFORMATION
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: Extract & Normalize Salary Information")
print("=" * 80)

print(f"\nAnalyzing salary data...")
print(f"Jobs with salary info: {df['min_salary'].notna().sum()}/{len(df)}")

# Convert salary columns to numeric
df['min_salary'] = pd.to_numeric(df['min_salary'], errors='coerce')
df['max_salary'] = pd.to_numeric(df['max_salary'], errors='coerce')
print(f"✓ Converted salary columns to numeric")

# Standardize salary_period
print(f"\nStandardizing salary periods...")
df['salary_period'] = df['salary_period'].replace({
    'YEAR': 'YEARLY',
    'MONTH': 'MONTHLY',
    'HOUR': 'HOURLY',
})
print(f"✓ Standardized salary periods to YEARLY, MONTHLY, HOURLY")

# Create derived salary fields
print(f"\nCreating derived salary fields...")

# Average salary (midpoint of min and max)
df['avg_salary'] = (df['max_salary'] + df['min_salary']) / 2
print(f"✓ Created avg_salary (midpoint of min and max)")

# Salary range (spread between min and max)
df['salary_range'] = df['max_salary'] - df['min_salary']
print(f"✓ Created salary_range (spread)")

# Display salary statistics
salary_with_data = df[df['min_salary'].notna()]
if len(salary_with_data) > 0:
    print(f"\nSalary statistics (for {len(salary_with_data)} jobs with data):")
    print(f"  Min salary: ${salary_with_data['min_salary'].min():,.0f} - ${salary_with_data['min_salary'].max():,.0f}")
    print(f"  Max salary: ${salary_with_data['max_salary'].min():,.0f} - ${salary_with_data['max_salary'].max():,.0f}")
    print(f"  Avg salary: ${salary_with_data['avg_salary'].mean():,.0f}")
    
# ============================================================================
# STEP 3: EXTRACT & CATEGORIZE REQUIRED SKILLS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: Extract & Categorize Required Skills")
print("=" * 80)

# Common skill keywords to look for in job descriptions
SKILL_CATEGORIES = {
    'Programming Languages': {
        'Python': r'\bpython\b',
        'R': r'\b(?:r\s+programming|r\slanguage)',
        'SQL': r'\bsql\b',
        'Java': r'\bjava\b',
        'JavaScript': r'\bjavascript\b',
        'C++': r'\bc\+\+\b',
        'C#': r'\bc#\b',
        'VBA': r'\bvba\b',
    },
    'Data Tools & Platforms': {
        'Tableau': r'\btableau\b',
        'Power BI': r'\bpower\s*bi\b',
        'Excel': r'\bexcel\b',
        'Jupyter': r'\bjupyter\b',
        'Hadoop': r'\bhadoop\b',
        'Spark': r'\bspark\b',
    },
    'Databases': {
        'PostgreSQL': r'\bpostgresql\b',
        'MySQL': r'\bmysql\b',
        'MongoDB': r'\bmongodb\b',
        'Oracle': r'\boracle\b',
        'SQL Server': r'\bsql\s*server\b',
    },
    'Soft Skills': {
        'Communication': r'\bcommunication\b',
        'Leadership': r'\bleadership\b',
        'Problem Solving': r'\bproblem[\s-]?solving\b',
        'Collaboration': r'\bcollaboration\b',
        'Project Management': r'\bproject\s*management\b',
    },
    'Analysis & Statistics': {
        'Statistical Analysis': r'\bstatistical\s*analysis\b',
        'Data Analysis': r'\bdata\s*analysis\b',
        'Predictive Modeling': r'\bpredictive\s*modeling\b',
        'Machine Learning': r'\bmachine\s*learning\b',
        'Data Visualization': r'\bdata\s*visualization\b',
    }
}

def extract_skills(text):
    """Extract skills from job description text"""
    if pd.isna(text):
        return []
    
    text = str(text).lower()
    found_skills = []

    for category, skills in SKILL_CATEGORIES.items():
        for skill, pattern in skills.items():
            if re.search(pattern, text):
                found_skills.append(skill)

    return found_skills

print(f"\nExtracting skills from job descriptions...")
df['skills'] = df['description'].apply(extract_skills)

# Coutn average skills per job
avg_skills = df['skills'].apply(len).mean()
print(f"✓ Extracted skills from {len(df)} jobs")
print(f"  Average skills per job: {avg_skills:.1f}")

# Most common skills
print(f"\nMost common skills found:")
all_skills = [skill for skills_list in df['skills'] for skill in skills_list]
skill_counts = Counter(all_skills)
for skill, count in skill_counts.most_common(10):
    print(f"  {skill}: {count} jobs")

# Create skill category columns
print(f"\nCreating skill category columns...")
for category in SKILL_CATEGORIES.keys():
    col_name = f'has_{category.lower().replace(" ", "_")}'
    df[col_name] = df['skills'].apply(
        lambda x: any(skill in SKILL_CATEGORIES[category] for skill in x)
    )
print(f"✓ Created {len(SKILL_CATEGORIES)} skill category columns")

# Display skill category summary
print(f"\nSkill Category Distribution:")
for category in SKILL_CATEGORIES.keys():
    col_name = f'has_{category.lower().replace(" ", "_")}'
    count = df[col_name].sum()
    pct = (count / len(df)) * 100
    print(f"  {category}: {count} jobs ({pct:.1f}%)")

# ============================================================================
# STEP 4: STANDARDIZE LOCATION DATA
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: Standardize Location Data")
print("=" * 80)

print(f"\nAnalyzing location data...")
print(f"Unique cities: {df['city'].nunique()}")
print(f"Unique states: {df['state'].nunique()}")
print(f"Unique countries: {df['country'].nunique()}")

# Standardize state names (convert abbreviations to full names)
STATE_ABBREVIATIONS = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
}

print(f"\nStandardizing state names...")
df['state'] = df['state'].replace(STATE_ABBREVIATIONS)
print(f"✓ Standardized state names to full names")

# Create full location string (city, state format)
df['location_standardized'] = df.apply(
    lambda row: f"{row['city']}, {row['state']}" if pd.notna(row['city']) and pd.notna(row['state']) else None,
    axis=1
)
print(f"✓ Created standardized location format (city, state)")

# Validate coordinates
print(f"\nValidating geographic coordinates...")
valid_coords = (
    (df['latitude'].notna()) &
    (df['longitude'].notna()) &
    (df['latitude'] >= -90) & (df['latitude'] <= 90) &
    (df['longitude'] >= -180) & (df['longitude'] <= 180)
).sum()
print(f"✓ Valid coordinates: {valid_coords}/{len(df)} jobs")

# Display location summary
print(f"\nLocation Summary:")
print(f"  Total jobs: {len(df)}")
print(f"  Jobs with location data: {df['location_standardized'].notna().sum()}")
print(f"  Remote jobs: {df['is_remote'].sum()}")
print(f"  On-site jobs: {(~df['is_remote']).sum()}")

print(f"\nTop 10 locations:")
for loc, count in df['location_standardized'].value_counts().head(10).items():
    print(f"  - {loc}: {count}")

# ============================================================================
# FINAL DATA VALIDATION & SAVE
# ============================================================================
print("\n" + "=" * 80)
print("FINAL DATA VALIDATION & SAVE")
print("=" * 80)

# Check for salary logic errors
salary_errors = (df['min_salary'] > df['max_salary']).sum()
print(f"\n✓ Salary logic errors (min > max): {salary_errors}")

# Check for required fields
print(f"\n✓ Required fields check:")
required = ['id', 'title', 'description', 'city', 'state', 'country']
for field in required:
    null_count = df[field].isnull().sum()
    status = "✓ PASS" if null_count == 0 else f"⚠ {null_count} missing"
    print(f"  {field}: {status}")

print("\n" + "=" * 80)
print("SAVING CLEANED DATA")
print("=" * 80)

# Save as CSV
csv_path = 'cleaned_jobs.csv'
df.to_csv(csv_path, index=False)
print(f"\n✓ Saved to: {csv_path}")

# Save as JSON
json_path = 'cleaned_jobs.json'
df.to_json(json_path, orient='records', indent=2)
print(f"✓ Saved to: {json_path}")

print(f"\n{'='*80}")
print(f"DAY 4 COMPLETE! ✓")
print(f"{'='*80}")

print(f"""
Summary:
  Original dataset: {len(raw_jobs)} rows
  Cleaned dataset: {len(df)} rows, {df.shape[1]} columns
  
Data Standardization:
  ✓ Field names simplified ({len(rename_mapping)} renamed)
  ✓ Salary normalized ({df['min_salary'].notna().sum()} jobs with salary data)
  ✓ Skills extracted ({len(all_skills)} total skills found across all jobs)
  ✓ Location standardized ({df['location_standardized'].notna().sum()} valid locations)
  ✓ {len(SKILL_CATEGORIES)} skill categories created
  
Next Steps:
  1. Review cleaned_jobs.csv
  2. Design PostgreSQL database (Day 3 schema ready)
  3. Load cleaned data into database
  4. Create Tableau visualizations
""")
