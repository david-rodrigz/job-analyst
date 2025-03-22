import os
from google import genai

gemini_api_key = os.getenv('GEMINI_API_KEY')

def extract_key_words(job_posting):
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        # contents='List a few popular cookie recipes. Be sure to include the amounts of ingredients.',
        contents=f'List all the keywords in the following job posting: \n{job_posting}',
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[str],
        },
    )
    # Return keyword list
    return response.parsed

def get_job_posting(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Skip the first line (heading) and join the rest of the lines to get the job posting content
    job_posting = ''.join(lines[1:]).strip()
    return job_posting

# Example job post
file_path = 'Job Posts/Data Engineer/Analytics_Data_Engineer.md'
job_posting = get_job_posting(file_path)

# Example keyword extraction
keywords = extract_key_words(job_posting)
print(keywords)