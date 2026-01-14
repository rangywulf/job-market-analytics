# JSearch API Response Structure Documentation

## Overview
JSearch API returns job listings from Google for Jobs, aggregating data from LinkedIn, Indeed, Glassdoor, and other job boards.

---

## Root Response Object

```json
{
  "data": [],
  "request_id": "string"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of job listing objects |
| `request_id` | string | Unique identifier for the API request |

---

## Job Object Fields

Each job in the `data` array contains the following fields:

### Basic Job Information

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_id` | string | `"HIfNNzO3XqO4iOkyAAAAAA=="` | Unique identifier for the job posting |
| `job_title` | string | `"Data Analyst (R or Stata) (Hybrid)"` | Job position title |
| `job_description` | string | Long text | Full job description with duties and requirements |
| `job_employment_type` | string | `"Full-time"` | Type of employment (Full-time, Part-time, Contract, etc.) |
| `job_employment_types` | array | `['FULLTIME']` | Array format of employment types |
| `job_is_remote` | boolean | `false` | Whether the job is remote |
| `job_posted_at` | string | `"22 hours ago"` | Human-readable posting time |
| `job_posted_at_timestamp` | integer | `1768348800` | Unix timestamp of posting |
| `job_posted_at_datetime_utc` | string | `"2026-01-14T00:00:00.000Z"` | ISO 8601 datetime format |

### Employer Information

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `employer_name` | string | `"Jobs via Dice"` | Company/employer name |
| `employer_logo` | string | URL | Logo image URL (may be null) |
| `employer_website` | string | URL or null | Company website (may be null) |
| `job_publisher` | string | `"LinkedIn"` | Platform where job was published |

### Location Information

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_location` | string | `"Washington, DC"` | Full location string |
| `job_city` | string | `"Washington"` | City name |
| `job_state` | string | `"District of Columbia"` | State/province name |
| `job_country` | string | `"US"` | Country code |
| `job_latitude` | float | `38.9072873` | Geographic latitude |
| `job_longitude` | float | `-77.0369274` | Geographic longitude |

### Salary Information

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_salary` | string or null | `"$50K-$70K"` | Salary range as string (may be null) |
| `job_min_salary` | integer or null | `50000` | Minimum salary in currency (may be null) |
| `job_max_salary` | integer or null | `70000` | Maximum salary in currency (may be null) |
| `job_salary_period` | string or null | `"YEARLY"` | Salary period: YEARLY, MONTHLY, HOURLY (may be null) |

### Application Information

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_apply_link` | string | URL | Direct link to apply for the job |
| `job_apply_is_direct` | boolean | `false` | Whether this is a direct application link |
| `apply_options` | array | See below | Array of different ways to apply |

#### Apply Options Structure

```json
{
  "publisher": "LinkedIn",
  "apply_link": "https://...",
  "is_direct": false
}
```

### Job Highlights

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_highlights` | object | See below | Structured highlights extracted from job posting |

#### Job Highlights Structure

```json
{
  "Qualifications": ["requirement 1", "requirement 2", ...],
  "Responsibilities": ["duty 1", "duty 2", ...],
  "Benefits": ["benefit 1", "benefit 2", ...] // May not always be present
}
```

### Classification Information

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_onet_soc` | integer | `43911100` | SOC (Standard Occupational Classification) code |
| `job_onet_job_zone` | integer | `4` | Job zone level (1-5, where 5 is highest skill requirement) |

### Additional Links

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `job_google_link` | string | URL | Google Jobs link to view the posting |
| `job_benefits` | string or null | Text | Job benefits (may be null) |

---

## Data Quality Notes

### Fields That May Be Null
- `employer_logo` - Not all employers have logos available
- `employer_website` - Some employers don't provide websites
- `job_salary` - Many jobs don't list salary publicly
- `job_min_salary` / `job_max_salary` - Rare to have numeric salary data
- `job_salary_period` - Only present if salary data exists
- `job_benefits` - Not always extracted or provided

### Fields That Are Always Present
- `job_id` - Unique identifier
- `job_title` - Job title
- `job_description` - Full description
- `employer_name` - Company name
- `job_apply_link` - Application link
- `job_location` - Location info
- `job_posted_at_datetime_utc` - Posting datetime

---

## API Response Pagination

The API returns jobs one page at a time. Each page contains approximately 10 job listings.

```python
params = {
    'query': 'Data Analyst',  # Search term
    'page': 1,               # Page number (1-indexed)
    'num_pages': 1           # Number of pages to fetch per request (set to 1)
}
```

To fetch multiple pages, increment the `page` parameter in a loop.

---

## Data Types Summary

| Type | Fields |
|------|--------|
| **String** | job_title, job_description, employer_name, job_location, job_city, job_state, job_country, job_apply_link, job_google_link, job_posted_at, job_posted_at_datetime_utc, job_published, job_salary, job_benefits |
| **Integer** | job_posted_at_timestamp, job_min_salary, job_max_salary, job_latitude, job_longitude, job_onet_soc, job_onet_job_zone |
| **Float** | job_latitude, job_longitude |
| **Boolean** | job_is_remote, job_apply_is_direct |
| **Array** | job_employment_types, apply_options, job_highlights (values are arrays) |
| **Object** | job_highlights, apply_options (items) |
| **Null-able** | employer_logo, employer_website, job_salary, job_min_salary, job_max_salary, job_salary_period, job_benefits |

---

## Key Fields for Analytics Pipeline

Based on this structure, these are the most useful fields for your analytics:

**Essential for Analysis:**
- `job_title` - What roles are in demand
- `job_description` & `job_highlights` - Extract required skills
- `employer_name` - Company hiring patterns
- `job_location` - Geographic distribution
- `job_min_salary` / `job_max_salary` - Salary trends
- `job_posted_at_datetime_utc` - Timing and trends
- `job_is_remote` - Remote vs on-site distribution

**Good to Have:**
- `job_employment_type` - Full-time vs contract
- `job_onet_job_zone` - Skill level requirement
- `job_state` / `job_country` - Location filtering

**Lower Priority:**
- `job_google_link` - Reference links
- `apply_options` - Multiple application sources
- `employer_website` - Company research