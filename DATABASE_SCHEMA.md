# PostgreSQL Database Schema Design
## Job Market Analytics Pipeline

---

## Design Principles

1. **Normalization**: Separate companies and skills into their own tables to avoid duplication
2. **Flexibility**: Handle optional fields (salary, benefits) gracefully
3. **Analytics-Ready**: Structure supports easy querying and aggregation
4. **Scalability**: Use proper indexes and constraints

---

## Tables

### 1. `companies` Table
Stores unique employer information to avoid duplication.

```sql
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    employer_name VARCHAR(255) NOT NULL UNIQUE,
    employer_website VARCHAR(500),
    employer_logo VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Rationale**: Multiple jobs can be from the same company. Store company info once and reference it.

---

### 2. `jobs` Table
Core job listing data. This is the main table for analytics.

```sql
CREATE TABLE jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(company_id),
    job_title VARCHAR(500) NOT NULL,
    job_description TEXT,
    job_location VARCHAR(255),
    job_city VARCHAR(100),
    job_state VARCHAR(100),
    job_country VARCHAR(2),
    job_latitude FLOAT,
    job_longitude FLOAT,
    job_is_remote BOOLEAN DEFAULT FALSE,
    job_employment_type VARCHAR(50),
    job_publisher VARCHAR(100),
    job_apply_link VARCHAR(500),
    job_apply_is_direct BOOLEAN,
    job_google_link VARCHAR(500),
    job_min_salary INTEGER,
    job_max_salary INTEGER,
    job_salary_period VARCHAR(20),
    job_onet_soc VARCHAR(20),
    job_onet_job_zone INTEGER,
    job_posted_at_timestamp BIGINT,
    job_posted_at_datetime_utc TIMESTAMP,
    job_posted_at_relative VARCHAR(50),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
```

**Indexes**:
```sql
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_city ON jobs(job_city);
CREATE INDEX idx_jobs_state ON jobs(job_state);
CREATE INDEX idx_jobs_is_remote ON jobs(job_is_remote);
CREATE INDEX idx_jobs_posted_at ON jobs(job_posted_at_datetime_utc);
CREATE INDEX idx_jobs_salary_range ON jobs(job_min_salary, job_max_salary);
```

---

### 3. `job_benefits` Table
Stores job benefits as a separate table (many-to-many relationship).

```sql
CREATE TABLE job_benefits (
    job_benefit_id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    benefit_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Index**:
```sql
CREATE INDEX idx_job_benefits_job_id ON job_benefits(job_id);
```

---

### 4. `skills` Table
Stores unique skills extracted from job highlights/descriptions.

```sql
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Skill Categories**: 
- Programming Languages (Python, R, SQL, etc.)
- Tools & Platforms (Tableau, Power BI, etc.)
- Databases (PostgreSQL, MySQL, etc.)
- Soft Skills (Communication, Leadership, etc.)
- Methodologies (Agile, etc.)

---

### 5. `job_skills` Table
Many-to-many relationship between jobs and required skills.

```sql
CREATE TABLE job_skills (
    job_skill_id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(skill_id),
    is_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, skill_id)
);
```

**Indexes**:
```sql
CREATE INDEX idx_job_skills_job_id ON job_skills(job_id);
CREATE INDEX idx_job_skills_skill_id ON job_skills(skill_id);
```

---

### 6. `job_highlights` Table
Stores structured qualifications, responsibilities, and other highlights.

```sql
CREATE TABLE job_highlights (
    highlight_id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    highlight_type VARCHAR(50),
    highlight_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Highlight Types**: 
- Qualifications
- Responsibilities
- Benefits (if not extracted to benefits table)

**Index**:
```sql
CREATE INDEX idx_job_highlights_job_id ON job_highlights(job_id);
```

---

## Entity Relationship Diagram

```
┌──────────────────┐
│   companies      │
├──────────────────┤
│ company_id (PK)  │
│ employer_name    │
│ employer_website │
│ employer_logo    │
└────────┬─────────┘
         │ (1:N)
         │
    ┌────▼──────────────────┐
    │       jobs            │
    ├───────────────────────┤
    │ job_id (PK)           │
    │ company_id (FK)       │
    │ job_title             │
    │ job_description       │
    │ job_location          │
    │ job_salary_*          │
    │ ...                   │
    └────┬─────────┬────────┘
         │         │ (1:N)
    (1:N)│         │
         │    ┌────▼──────────────────┐
    ┌────▼────┴┐ job_skills/benefits│
    │ (many-to-many junctions)       │
    └───────────────────────────────┘
```

---

## Data Types Summary

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| job_id | VARCHAR(255) | NO | Unique API ID |
| company_id | INTEGER | NO | Foreign key to companies |
| job_title | VARCHAR(500) | NO | Job title |
| job_description | TEXT | NO | Full job description |
| job_location | VARCHAR(255) | NO | City, State format |
| job_latitude/longitude | FLOAT | NO | Geographic coordinates |
| job_is_remote | BOOLEAN | NO | Default FALSE |
| job_min_salary | INTEGER | YES | NULL if not provided (~55%) |
| job_max_salary | INTEGER | YES | NULL if not provided (~55%) |
| job_salary_period | VARCHAR(20) | YES | YEARLY, MONTHLY, HOURLY |
| job_posted_at_datetime_utc | TIMESTAMP | YES | ISO format timestamp |
| job_benefits | (separate table) | N/A | Many-to-many |

---

## Key Analytics Queries This Supports

1. **Salary by Location**
```sql
SELECT job_city, AVG(job_min_salary), AVG(job_max_salary), COUNT(*) 
FROM jobs 
WHERE job_min_salary IS NOT NULL 
GROUP BY job_city;
```

2. **Most In-Demand Skills**
```sql
SELECT s.skill_name, COUNT(*) as demand_count
FROM job_skills js
JOIN skills s ON js.skill_id = s.skill_id
GROUP BY s.skill_name
ORDER BY demand_count DESC;
```

3. **Remote vs On-Site Distribution**
```sql
SELECT job_is_remote, COUNT(*) 
FROM jobs 
GROUP BY job_is_remote;
```

4. **Jobs by Company**
```sql
SELECT c.employer_name, COUNT(*) as job_count
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
GROUP BY c.employer_name
ORDER BY job_count DESC;
```

5. **Salary vs Required Skills**
```sql
SELECT s.skill_name, AVG(j.job_min_salary), AVG(j.job_max_salary)
FROM jobs j
JOIN job_skills js ON j.job_id = js.job_id
JOIN skills s ON js.skill_id = s.skill_id
WHERE j.job_min_salary IS NOT NULL
GROUP BY s.skill_name
ORDER BY AVG(j.job_min_salary) DESC;
```

---

## Migration Strategy

1. Create tables in this order: `companies` → `jobs` → `skills` → `job_skills` → `job_benefits` → `job_highlights`
2. Use transactions to ensure data consistency
3. Add indexes after data loading for better performance
4. Implement foreign key constraints to maintain referential integrity

---

## Notes on Normalization

- **Companies**: Separated to avoid storing duplicate company info with each job
- **Skills**: Separated to allow analysis of which skills are most in-demand
- **Benefits**: Separated as jobs can have multiple benefits
- **Highlights**: Separated to store structured qualifications/responsibilities

This design makes it easy to aggregate and analyze the job market data from multiple angles!