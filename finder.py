import requests
from bs4 import BeautifulSoup
import openai
import subprocess
import os
import sys

# Get keys and tokens from environment variables
API_KEY = os.environ.get('GOOGLE_API_KEY')
CSE_ID = os.environ.get('GOOGLE_CSE_ID')
github_token = os.environ.get('GITHUB_API_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not (API_KEY and CSE_ID and github_token and OPENAI_API_KEY):
    sys.exit("API keys or tokens not set. Please refer to the README for configuration instructions.")

def google_search(query):
    try:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': query,
            'key': API_KEY,
            'cx': CSE_ID
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error performing Google search: {e}")
        return None

def get_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return ' '.join([p.text for p in soup.find_all('p')])
    except requests.RequestException as e:
        #print(f"Error fetching article content from {url}: {e}")
        return ''

def ask_chatgpt(questions):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=questions
        )
        answer_text = response.choices[0].message.content
        #print(f"GPT ANSWER: {answer_text}\n")
        return answer_text
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

def search_github_code(query, organization):
    try:
        url = "https://api.github.com/search/code"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {
            "q": f"{query} org:{organization} extension:sol",
            "per_page": 10,
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error searching GitHub: {e}")
        return None

def clone_repository(repo_url):
    try:
        subprocess.run(["git", "clone", repo_url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_url}: {e}")

def search_git_log(function_name, repo_path):
    try:
        os.chdir(repo_path)
        command = ["git", "log", "-S", f"{function_name}", "--pretty=format:'%H %an'"]
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        #print(f"Raw output: {result.stdout}")
        commits = result.stdout.split('\n')
        if commits and commits[-1]:
            commit_info = commits[-1].strip("'").split(' ', 1)
            if len(commit_info) == 2:
                first_commit, author_name = commit_info
                print(f"First commit introducing the function: {first_commit}")
                print(f"Author name: {author_name}")
                return True
            else:
                print(f"Unexpected git log format: {commits[0]}")
                return False
        else:
            print(f"No commits found introducing the function {function_name}.")
            return False
    except FileNotFoundError:
        print(f"Directory not found: {repo_path}")
        return False
    
def formulate_question(article_content):
    question = "These are combinations of some articles about a web3 project vulnerability. Each article starts with 'ARTICLE'. Could you please deduct the name of the vulnerable function that hackers abused? Please just return the name of the function as your response and nothing else. If you cannot find the function name, say 'No vuln fnc is found'"
    question += article_content
    return question

def get_clone_url(repo_url):
    try:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        response = requests.get(repo_url, headers=headers)
        response.raise_for_status()
        return response.json().get('clone_url')
    except requests.RequestException as e:
        print(f"Error getting clone URL from {repo_url}: {e}")
        return None

def main():
    project_name = input("Enter the cryptocurrency project name: ")
    org_name = input("Enter the name of the organization on GitHub: ")
    query = f"{project_name} hacked"
    
    # Search using Google
    results = google_search(query)

    all_article_content = ""
    function_name = ""
    links = [item['link'] for item in results.get('items', [])]

    while links:
        url = links.pop(0)
        #print(f"Checking {url}")

        article_content = "ARTICLE\n" + get_article_content(url) + "\n"

        if len(all_article_content) + len(article_content) <= 10000:
            all_article_content += article_content
        else:
            #print(f"Character limit reached. Asking GPT-3 with current content.")
            questions = [{"role": "system", "content": "You are a intelligent assistant."}]
            question = formulate_question(all_article_content)
            questions.append({"role": "user", "content": question})
            function_name = ask_chatgpt(questions)

            if function_name and function_name != "No vuln fnc is found":
                function_name = "function " + function_name + "("
                print(f"Vulnerable function: {function_name}")
                break
            else:
                print("No function name found in the article. Continuing with next set of links.")
                all_article_content = ""
                continue

    # Search for the code in GitHub
    github_results = search_github_code(f"function {function_name}", org_name)
    
    if github_results['items'] != []:
        for item in github_results['items']:
            print(f"Repository: {item['repository']['full_name']}")
            print(f"File: {item['name']}")
            print(f"URL: {item['html_url']}\n")
            repo_url = get_clone_url(item['repository']['url'])
            if repo_url:
                print(f"Cloning repository {repo_url}...")
                clone_repository(repo_url)
                print(f"Repository {repo_url} cloned successfully.\n")
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                if search_git_log(function_name, repo_name):
                    break
    else:
        print("No results found on Github.")


if __name__ == "__main__":
    main()
