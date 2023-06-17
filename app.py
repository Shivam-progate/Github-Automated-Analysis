
import requests
import re
import langchain
import openai

# Set up OpenAI GPT API credentials
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Function to fetch a GitHub user's repositories
def fetch_user_repos(username):
    url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch user repositories. Status code: {response.status_code}")

# Function to assess repository complexity using GPT and LangChain
def assess_repository(repo):
    # Retrieve repository information
    repo_name = repo['name']
    repo_url = repo['html_url']
    readme_url = f"{repo_url}/blob/master/README.md"

    # Fetch the README content
    readme_response = requests.get(readme_url)
    readme_content = ''
    if readme_response.status_code == 200:
        readme_content = readme_response.text

    # Analyze README content using GPT
    gpt_input = f"Assess the complexity of repository {repo_name}. {readme_content}"
    gpt_response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=gpt_input,
        max_tokens=100,
        temperature=0.5
    )
    complexity_score = gpt_response.choices[0].score

    # Analyze repository code using LangChain
    code_metrics = langchain.extract_metrics_from_github_repo(repo_url)

    # Calculate the overall complexity score based on GPT and LangChain metrics
    overall_score = complexity_score + code_metrics.complexity_score

    return repo_name, repo_url, overall_score

# Function to find the most technically challenging repository
def find_most_challenging_repository(username):
    try:
        # Fetch user repositories
        repositories = fetch_user_repos(username)

        if not repositories:
            raise Exception(f"No repositories found for user {username}")

        # Assess complexity for each repository
        repository_scores = []
        for repo in repositories:
            repo_name, repo_url, overall_score = assess_repository(repo)
            repository_scores.append((repo_name, repo_url, overall_score))

        # Sort repositories by score in descending order
        repository_scores.sort(key=lambda x: x[2], reverse=True)

        # Return the most challenging repository
        return repository_scores[0]

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
github_username = 'Shivam-progate'
most_challenging_repo = find_most_challenging_repository(github_username)
if most_challenging_repo:
    print(f"The most challenging repository for user {github_username} is:")
    print(f"Name: {most_challenging_repo[0]}")
    print(f"URL: {most_challenging_repo[1]}")
