import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class JSearchClient:
    """Client for interacting with the JSearch API."""

    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('RAPIDAPI_HOST')
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        
        if not self.api_key or not self.api_host:
            raise ValueError("API credentials not found in .env file")
    
    def get_headers(self):
        """Return headers for the API request."""
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
    
    def search_jobs(self, query, page=1, num_pages=1):
        """Search for jobs using the JSearch API.

        Args:
            query (str): The search query.
            page (int): The page number to retrieve.
            num_pages (int): The number of pages to retrieve.

        Returns:
            list: A list of job postings.
        """
        all_jobs = []
        
        for page_num in range(page, page + num_pages):
            print(f"Fetching page {page_num}...")
            params = {
                "query": query,
                "page": page_num,
                "num_pages": 1
            }
            
            try:
                response = requests.get(
                    self.base_url,
                    headers=self.get_headers(),
                    params=params,
                    timeout=10
                )

                # Check if request was successful
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get('data', [])
                    all_jobs.extend(jobs)
                    print(f"  Successfully fetched {len(jobs)} jobs from page {page_num}")
                else:
                    print(f"  Error on page {page_num}: Status code {response.status_code}")
                    print(f"  Response: {response.text}")

            except requests.exceptions.Timeout:
                print(f"  Timeout error on page {page_num}")
            except requests.exceptions.RequestException as e:
                print(f"  Request error on page {page_num}: {e}")
            except json.JSONDecodeError:
                print(f"  JSON decode error on page {page_num}")
        
        return all_jobs
    
    def save_jobs_to_json(self, jobs, filename='raw_jobs.json'):
        """Save job postings to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            print(f"\nSuccessfully saved {len(jobs)} jobs to {filename}")
        except IOError as e:
            print(f"Error saving jobs to file: {e}")

    def print_sample_job(self, jobs):
        """Print a sample job posting."""
        if jobs:
            print("\n" + "="*80)
            print("Sample Job Posting:")
            print("="*80)
            sample = jobs[0]
            for key, value in sample.items():
                print(f"{key}: {value}")
            print("="*80)
        else:
            print("No jobs found to display.")
    
def main():
    """Main function to test the API"""

    try:
        # Initialize client
        client = JSearchClient()
        print("✓ API credentials loaded successfully\n")

        #Search for data analytics jobs
        print("Searching for 'Data Analyst' jobs...")
        jobs = client.search_jobs(query="Data Analyst", num_pages=3)

        # Print Results
        print(f"\n✓ Total jobs fetched: {len(jobs)}")

        # Show sample job structure
        client.print_sample_job(jobs)

        #save to JSON
        client.save_jobs_to_json(jobs)

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Make sure your .env file has RAPIDAPI_KEY and RAPIDAPI_HOST")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
        
