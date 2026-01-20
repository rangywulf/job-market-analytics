import json

def analyze_jobs_data(filename='raw_jobs.json'):
    """Analyze the structure and content of the jobs JSON file"""
    
    # Load the data
    with open(filename, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    print("\n" + "="*80)
    print(f"DATA ANALYSIS FOR: {filename}")
    print("="*80 + "\n")
    
    print(f"Total jobs: {len(jobs)}\n")
    
    if len(jobs) == 0:
        print("No jobs to analyze")
        return
    
    # Get all unique field names
    all_fields = set()
    for job in jobs:
        all_fields.update(job.keys())
    
    all_fields = sorted(list(all_fields))
    
    print(f"Total unique fields: {len(all_fields)}\n")
    print("="*80)
    print("FIELD ANALYSIS")
    print("="*80 + "\n")
    
    # Analyze each field
    field_stats = {}
    
    for field in all_fields:
        stats = {
            'present_count': 0,
            'null_count': 0,
            'data_types': set(),
            'sample_values': []
        }
        
        for job in jobs:
            if field in job:
                value = job[field]
                stats['present_count'] += 1
                
                if value is None:
                    stats['null_count'] += 1
                else:
                    value_type = type(value).__name__
                    stats['data_types'].add(value_type)
                    
                    if len(stats['sample_values']) < 1:
                        if isinstance(value, (list, dict)):
                            stats['sample_values'].append(str(value)[:80])
                        else:
                            stats['sample_values'].append(str(value)[:80])
        
        field_stats[field] = stats
    
    # Print detailed analysis
    for field in all_fields:
        stats = field_stats[field]
        present_pct = (stats['present_count'] / len(jobs)) * 100
        null_pct = (stats['null_count'] / len(jobs)) * 100
        
        print(f"Field: {field}")
        print(f"  Present: {stats['present_count']}/{len(jobs)} ({present_pct:.1f}%)")
        print(f"  Null/None: {stats['null_count']}/{len(jobs)} ({null_pct:.1f}%)")
        print(f"  Data Type(s): {', '.join(sorted(stats['data_types']))}")
        
        if stats['sample_values']:
            print(f"  Sample: {stats['sample_values'][0]}")
        
        print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    always_present = [f for f in all_fields if field_stats[f]['present_count'] == len(jobs)]
    mostly_null = [f for f in all_fields if field_stats[f]['present_count'] < len(jobs) * 0.5]
    
    print(f"Fields always present ({len(always_present)}):")
    for field in always_present:
        print(f"  - {field}")
    
    print(f"\nFields mostly null/missing ({len(mostly_null)}):")
    for field in mostly_null:
        present_count = field_stats[field]['present_count']
        present_pct = (present_count / len(jobs)) * 100
        print(f"  - {field} ({present_pct:.1f}%)")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    analyze_jobs_data()