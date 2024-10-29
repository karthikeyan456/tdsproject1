import requests
import csv

GITHUB_TOKEN = "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"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_users(query, per_page=100):
    """Fetch users from GitHub based on the query."""
    users = []
    page = 1

    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        print(f"Fetching page {page}...")

        if response.status_code != 200:
            print("Error fetching data:", response.json())
            break

        data = response.json()
        users.extend(data['items'])

        if len(data['items']) < per_page:
            break

        page += 1

    return users

def get_user_details(username):
    """Fetch detailed information about a user."""
    user_url = f"https://api.github.com/users/{username}"
    user_data = requests.get(user_url, headers=HEADERS).json()

    return {
        'login': user_data['login'],
        'name': user_data.get('name', ''),
        'company': clean_company_name(user_data.get('company')),
        'location': user_data.get('location', ''),
        'email': user_data.get('email', ''),
        'hireable': user_data.get('hireable', False),
        'bio': user_data.get('bio', ''),
        'public_repos': user_data.get('public_repos', 0),
        'followers': user_data.get('followers', 0),
        'following': user_data.get('following', 0),
        'created_at': user_data.get('created_at', ''),
    }

def clean_company_name(company):
    """Clean and standardize company names."""
    if company:
        company = company.strip().upper()
        if company.startswith('@'):
            company = company[1:]
    return company

def get_user_repos(username):
    """Fetch repositories for a given user."""
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=500"
    response = requests.get(repos_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching repos for {username}: {response.json()}")
        return []

    repos_data = response.json()
    return [
        {
            'login': username,
            'full_name': repo['full_name'],
            'created_at': repo['created_at'],
            'stargazers_count': repo['stargazers_count'],
            'watchers_count': repo['watchers_count'],
            'language': repo['language'],
            'has_projects': repo['has_projects'],
            'has_wiki': repo['has_wiki'],
            'license_name': repo['license']['key'] if repo['license'] else None,
        }
        for repo in repos_data
    ]

def save_to_csv(filename, data, fieldnames):
    """Save a list of dictionaries to a CSV file."""
    with open(filename, mode='w', encoding="utf-8", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    """Main function to execute the script."""
    query = "location:Chennai+followers:>50"
    users = fetch_users(query)
    
    detailed_users = [get_user_details(user['login']) for user in users]
    save_to_csv('usersa.csv', detailed_users, ['login', 'name', 'company', 'location', 'email', 'hireable', 'bio', 'public_repos', 'followers', 'following', 'created_at'])

    all_repos = []
    for user in detailed_users:
        repos = get_user_repos(user['login'])
        all_repos.extend(repos)

    save_to_csv('repositoriesa.csv', all_repos, ['login', 'full_name', 'created_at', 'stargazers_count', 'watchers_count', 'language', 'has_projects', 'has_wiki', 'license_name'])

    print("Done")

if __name__ == "__main__":
    main()
