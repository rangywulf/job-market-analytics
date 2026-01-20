import json

with open('raw_jobs.json') as f:
    jobs = json.load(f)

print(f"Total jobs loaded: {len(jobs)}")
print(f"First job ID: {jobs[0]['job_id']}")
print("Sample fields from first job:")
for key in list(jobs[0].keys())[:5]:
    print(f"  {key}")