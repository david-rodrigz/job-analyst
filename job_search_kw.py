import os
import time
import requests
from bs4 import BeautifulSoup
import sys
import json
from google import genai
from google.genai import errors

gemini_api_key = os.getenv('GEMINI_API_KEY')

def extract_key_words(job_description):
    client = genai.Client(api_key=gemini_api_key)
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            # contents='List a few popular cookie recipes. Be sure to include the amounts of ingredients.',
            contents=f'List all the keywords in the following job description: \n{job_description}',
            config={
                'response_mime_type': 'application/json',
                'response_schema': list[str],
            },
        )
        # Return keyword list
        return response.parsed
    except errors.APIError as e:
        print(e.code)
        print(e.message)
        return [f'{e.code}: {e.message}']
        # if e.code == 503:
        #     print(e.code)
        #     print(e.message)
        #     return [f'Error ']

# Function for searching a job title, returns list of jobPostingIds
def query_jobs(search_query, location='United States'):
    job_posting_ids = []
    jobs_endpoint = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings'
    # GET request jobs
    query_params = {
        'keywords': search_query,
        'location': location
    }
    encoded_query_params = requests.models.RequestEncodingMixin._encode_params(query_params)
    results_page = requests.get(f'{jobs_endpoint}/search?{encoded_query_params}').text
    # Scrape jobPostingIds
    data = BeautifulSoup(results_page, 'html.parser')
    job_results = data.find_all('li')
    for job in job_results:
        job_div = job.find('div')
        job_id = job_div['data-entity-urn'].split(':')[-1]
        job_posting_ids.append(job_id)
    # Return list of job IDs
    print(f'Job Posting Ids: {job_posting_ids}')
    return job_posting_ids

# Get user arguments
num_arguments = len(sys.argv)

# Verify that only one argument is passed
if (num_arguments != 2):
    print('Usage: python job_search_kw.py <search_query>')
    sys.exit

# Job search query
job_search_query = sys.argv[1].strip()

# Scrape relevant jobPostingIds from LinkedIn
job_results = query_jobs(job_search_query)
print(f'Queried jobs for \'{job_search_query}\'')

# LinkedIn web scraping constants
job_posting_endpoint = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting'
title_class_filter = 'topcard__link'
posting_class_filter = 'show-more-less-html__markup'

# List to store job information
job_info_list = []

# Extract keywords from each job result
for job_id in job_results:
    job_page = requests.get(f'{job_posting_endpoint}/{job_id}').text
    data = BeautifulSoup(job_page, 'html.parser')

    # Extract job information
    job_title = data.find('a', class_=title_class_filter)
    job_title_text = job_title.text.strip()
    job_title_link = job_title['href']
    job_description = data.find('div', class_=posting_class_filter).text
    job_keywords = extract_key_words(job_description)

    # Append job information to the list
    job_info_list.append({
        'title': job_title_text,
        'id': job_id,
        'link': job_title_link,
        'description': job_description,
        'keywords': job_keywords
    })
    print(f'Successfully mined job #{job_id}')

# Save job information to a JSON file
with open(f'Job Posts/{job_search_query}.json', 'w') as json_file:
    json.dump(job_info_list, json_file, indent=4)

print(f"Job information saved to Job Posts/{job_search_query}.json")