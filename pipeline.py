import time
import json
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

def append_to_json_file(file_path, new_data):
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the existing data
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        # If the file does not exist, start with an empty list
        data = []

    # Append the new data
    data.append(new_data)

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def mine_keywords(job_folder_path):
    for job_title in os.listdir(job_folder_path):
        job_posting_path = os.path.join(job_folder_path, job_title)
        job_posting = get_job_posting(job_posting_path)
        # Extract keywords
        keywords = extract_key_words(job_posting)
        # save data
        data = {job_title: keywords}
        append_to_json_file('keywords.json', data)

# Example keyword mining
job_folder_path = 'Job Posts/Data Engineer'
mine_keywords(job_folder_path)