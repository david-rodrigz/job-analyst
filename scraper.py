import os
import requests
from bs4 import BeautifulSoup
import re
from markdownify import markdownify as md

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
    return job_posting_ids

# Function for retrieving and storing each job post in the 'Job Posts' folder
def get_job_postings(job_posting_ids, folder_name):
    jobs_folder_path = 'Job Posts'
    job_posting_endpoint = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting'
    title_class_filter = 'topcard__link'
    posting_class_filter = 'show-more-less-html__markup'

    for job_id in job_posting_ids:
        job_page = requests.get(f'{job_posting_endpoint}/{job_id}').text
        data = BeautifulSoup(job_page, 'html.parser')

        job_title = data.find('a', class_=title_class_filter)
        job_title_text = job_title.text.strip()
        job_title_link = job_title['href']
        job_posting_html = data.find('div', class_=posting_class_filter).prettify()
        
        # Convert HTML to Markdown
        job_posting_md = md(job_posting_html)

        file_friendly_title = re.sub(r'[^\w\s-]', '', job_title_text).strip().replace(' ', '_')

        folder_path = f'{jobs_folder_path}/{folder_name}'
        os.makedirs(folder_path, exist_ok=True)

        # Create the markdown file
        markdown_file_path = os.path.join(folder_path, f'{file_friendly_title}.md')
        with open(markdown_file_path, 'w') as file:
            file.write(f'# [{job_title_text}]({job_title_link})\n\n')
            file.write(job_posting_md)

# Example Run
search_query='Data Engineer'
job_posting_ids = query_jobs(search_query)
get_job_postings(job_posting_ids, search_query)