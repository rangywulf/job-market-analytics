import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JSearchClient:
    """Client for interacting with JSearch API"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('RAPIDAPI_HOST')
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.rate_limit_delay = 0.5  # Delay between requests (seconds)
        
        if not self.api_key or not self.api_host:
            raise ValueError("API credentials not found in .env file")
    
    def get_headers(self):
        """Return headers for API requests"""
        return {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.api_host
        }
    
    def search_jobs(self, query, num_pages=1, page=1):
        """
        Search for jobs using JSearch API with error handling and rate limiting
        
        Args:
            query (str): Job search query (e.g., "Data Analyst")
            num_pages (int): Number of pages to fetch
            page (int): Starting page number
        
        Returns:
            list: List of job listings
        """
        all_jobs = []
        failed_pages = []
        
        for page_num in range(page, page + num_pages):
            print(f"Fetching page {page_num}...")
            
            params = {
                'query': query,
                'page': page_num,
                'num_pages': 1
            }
            
            try:
                response = requests.get(
                    self.base_url,
                    headers=self.get_headers(),
                    params=params,
                    timeout=10
                )
                
                # Check for rate limiting (429 Too Many Requests)
                if response.status_code == 429:
                    print(f"  Rate limited on page {page_num}. Waiting before retry...")
                    time.sleep(2)  # Wait 2 seconds before retrying
                    # Retry once
                    response = requests.get(
                        self.base_url,
                        headers=self.get_headers(),
                        params=params,
                        timeout=10
                    )
                
                # Check if request was successful
                if response.status_code == 200:
                    try:
                        data = response.json()
                        jobs = data.get('data', [])
                        all_jobs.extend(jobs)
                        print(f"  ✓ Successfully fetched {len(jobs)} jobs from page {page_num}")
                    except json.JSONDecodeError as e:
                        print(f"  ✗ Error decoding JSON on page {page_num}: {e}")
                        failed_pages.append(page_num)
                        
                elif response.status_code == 401:
                    print(f"  ✗ Authentication failed - check your API credentials")
                    raise ValueError("Invalid API credentials")
                    
                elif response.status_code == 403:
                    print(f"  ✗ Access forbidden - you may have exceeded your quota")
                    break
                    
                else:
                    print(f"  ✗ Error on page {page_num}: Status code {response.status_code}")
                    failed_pages.append(page_num)
                    
            except requests.exceptions.Timeout:
                print(f"  ✗ Timeout error on page {page_num} - connection took too long")
                failed_pages.append(page_num)
                
            except requests.exceptions.ConnectionError as e:
                print(f"  ✗ Connection error on page {page_num}: {e}")
                failed_pages.append(page_num)
                
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Request error on page {page_num}: {e}")
                failed_pages.append(page_num)
            
            # Rate limiting - wait between requests
            if page_num < page + num_pages - 1:
                time.sleep(self.rate_limit_delay)
        
        # Summary
        print(f"\nFetch Summary:")
        print(f"  Total jobs fetched: {len(all_jobs)}")
        if failed_pages:
            print(f"  Failed pages: {failed_pages}")
        
        return all_jobs
    
    def save_jobs_to_json(self, jobs, filename='raw_jobs.json'):
        """Save job listings to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            print(f"\nSuccessfully saved {len(jobs)} jobs to {filename}")
        except IOError as e:
            print(f"Error saving to file: {e}")
    
    def print_sample_job(self, jobs):
        """Print a sample job to inspect the data structure"""
        if jobs:
            print("\n" + "="*80)
            print("SAMPLE JOB LISTING:")
            print("="*80)
            sample = jobs[0]
            for key, value in sample.items():
                print(f"{key}: {value}")
            print("="*80)
        else:
            print("No jobs to display")


def main():
    """Main function to test the API"""
    
    try:
        # Initialize client
        client = JSearchClient()
        print("✓ API credentials loaded successfully\n")

        # Search for data analytics jobs across multiple US locations
        locations = [
            'United States',
            'New York',
            'San Francisco',
            'Chicago',
            'Austin',
            'Seattle',
            'Boston',
            'Denver',
            'Atlanta',
            'Los Angeles'
        ]
        
        # Search for multiple data analytics job titles
        search_queries = [
            'Data Analyst',
            'Analytics Engineer',
            'Business Analyst',
            'Data Engineer',
            'BI Developer'
        ]
        
        all_jobs = []
        
        # Search each location with selected job titles
        for location in locations:
            for title in search_queries:
                search_query = f"{title} {location}"
                print(f"\nSearching for '{search_query}'...")
                jobs = client.search_jobs(query=search_query, num_pages=2)
                all_jobs.extend(jobs)
                print(f"  Found {len(jobs)} jobs | Running total: {len(all_jobs)}\n")
        
        # Print results
        print(f"\n{'='*80}")
        print(f"✓ Total jobs fetched across all searches: {len(all_jobs)}")
        print(f"{'='*80}\n")
        
        # Show sample job structure
        client.print_sample_job(all_jobs)
        
        # Save to JSON
        client.save_jobs_to_json(all_jobs, filename='raw_jobs.json')
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Make sure your .env file has RAPIDAPI_KEY and RAPIDAPI_HOST")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()