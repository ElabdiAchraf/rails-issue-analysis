import requests
import json
import pandas as pd

# Constants
BASE_URL = "https://api.github.com/repos/rails/rails/issues"
HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
PARAMS = {
    "state": "all",  # to get both open and closed issues
    "per_page": 100  # maximum issues per page
}

# Fetching data
issues = []
for page in range(1, 6):  # 5 pages to get 500 issues
    response = requests.get(BASE_URL, headers=HEADERS, params={**PARAMS, "page": page})
    if response.status_code == 200:
        issues.extend(response.json())
    else:
        print(f"Failed to fetch page {page}. Status code: {response.status_code}")

# Now, `issues` contains the last 500 issues from the Rails repo

print(f"Fetched {len(issues)} issues.")

# Saving the issues to a JSON file 
with open("rails_issues.json", "w") as f:
    json.dump(issues, f)

# Converting the issues list to a DataFrame

df_issues = pd.DataFrame(issues)
print(df_issues.head()) 