import requests
import os
import re
from bs4 import BeautifulSoup  # For extracting plain text from Markdown/HTML

# List of GitHub repository links
github_links = [
"https://github.com/deepankarvarma/To-Do-List-Using-Python",

"https://github.com/MaxRohowsky/chrome-dinosaur",
"https://github.com/wasimtikki120/WeatherVista-Interactive-Weather-App",

"https://github.com/Rohit-Nandagawali/HTML-Chat-Application-using-java",

"https://github.com/bqubique/Text-Editor",
"https://github.com/Malavikkarajmohan/Movie-Ticket-Booking-System",
"https://github.com/rba1aji/Job-Portal-System"]
def get_default_branch(repo_owner, repo_name):
    """Fetches the default branch of a GitHub repository."""
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json().get("default_branch", "main")  # Default to 'main'
    else:
        raise ValueError(f"Failed to fetch default branch for {repo_owner}/{repo_name}")

def fetch_readme_content(repo_url, index):
    """Fetches, extracts, and saves textual content from the README file of a GitHub repo."""
    repo_owner, repo_name = repo_url.rstrip('/').split('/')[-2:]

    # Get default branch dynamically
    default_branch = get_default_branch(repo_owner, repo_name)

    # Construct the README raw file URL
    raw_readme_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{default_branch}/README.md"

    # Fetch README content
    response = requests.get(raw_readme_url)
    if response.status_code != 200:
        print(f"README not found for {repo_url}")
        return
    
    readme_content = response.text

    # Extract textual content (remove Markdown syntax)
    plain_text = extract_text_from_markdown(readme_content)

    # Save to file
    file_name = f"evaluation/eval_files/eval_files{index}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(plain_text)

    print(f"Saved README content to {file_name}")

def extract_text_from_markdown(markdown_text):
    """Removes Markdown syntax and extracts plain text."""
    # Remove Markdown links/images (e.g., ![alt text](url) and [text](url))
    markdown_text = re.sub(r"!\[.*?\]\(.*?\)", "", markdown_text)  
    markdown_text = re.sub(r"\[.*?\]\(.*?\)", "", markdown_text)

    # Remove special formatting (bold, italic, inline code)
    markdown_text = re.sub(r"[*_`]", "", markdown_text)

    # Convert headers into plain text by stripping #
    markdown_text = re.sub(r"#+\s*", "", markdown_text)

    # Convert Markdown lists to plain text
    markdown_text = re.sub(r"^\s*[-*]\s+", "", markdown_text, flags=re.MULTILINE)

    # Remove extra spaces and HTML tags
    markdown_text = BeautifulSoup(markdown_text, "html.parser").get_text()
    
    return markdown_text.strip()

# Process each GitHub repo in the list
for i, repo_link in enumerate(github_links):
    fetch_readme_content(repo_link, i)
