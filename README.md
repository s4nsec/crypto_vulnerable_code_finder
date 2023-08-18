# crypto_vulnerable_code_finder

This tool is designed to search for information related to the vulnerabilities of cryptocurrency projects. It leverages Google's Custom Search Engine (CSE) to find relevant articles, extracts the details of vulnerabilities, and searches for corresponding code on GitHub. The tool further allows cloning of repositories and searching git logs for specific functions.

## Features

- Google Search: Searches for articles related to cryptocurrency project vulnerabilities using Google CSE.
- Article Content Extraction: Extracts and processes the content of articles.
- OpenAI Interaction: Formulates questions and asks ChatGPT for vulnerability details.
- GitHub Code Search: Searches for specific code snippets within a GitHub organization.
- Repository Cloning: Clones specific repositories from GitHub.
- Git Log Search: Searches git logs for specific function introductions.

## Setup
### Requirements
- Python 3.x
- requests
- BeautifulSoup
- openai

## Installing Dependencies
Install the required libraries using pip:
```bash
pip install requests beautifulsoup4 openai
```

## Configuration
Sensitive information like API keys and tokens should be stored in environment variables:
```bash
export GOOGLE_API_KEY='your_google_api_key'
export GOOGLE_CSE_ID='your_google_cse_id'
export GITHUB_TOKEN='your_github_token'
```

## OpenAI Configuration
Ensure that the OpenAI library is properly configured with your API key.

# Running the tool
Run the main script:
```bash
python finder.py
```
You will be prompted to enter the cryptocurrency project name and the name of the organization on GitHub.
