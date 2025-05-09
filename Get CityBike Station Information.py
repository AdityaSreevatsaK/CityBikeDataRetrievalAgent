import os
import subprocess
import requests
import pytz
import time
import logging
from datetime import datetime
from github import Github

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
start_time = time.time()

# 1. Fetch the Citi Bike station status data
station_status_url = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
try:
    response = requests.get(station_status_url)
    response.raise_for_status()
    data = response.json()
    logging.info("Fetched station status data successfully.")
except requests.exceptions.RequestException as e:
    logging.error(f"Failed to fetch data: {e}")
    data = {}

# 2. Determine current date and time in New York
ny_tz = pytz.timezone("America/New_York")
now = datetime.now(ny_tz)
date_str = now.strftime("%d-%m-%Y")
time_str = now.strftime("%H-%M-%S")  # e.g. "14-05-30"
logging.info(f"Current New York time: {date_str} {time_str}")

# 3. Create directory for today's date
folder_name = date_str
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 4. Save data to a file named by date and time
file_name = f"{folder_name}/{date_str}_Hour-{time_str}.txt"
with open(file_name, "w") as f:
    f.write(str(data))

# 5. Set up Git user config for Actions
subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)

# 6. Create a new branch with a unique timestamp-based name
branch_name = f"data-update-{date_str}-{time_str}"
subprocess.run(["git", "checkout", "-b", branch_name], check=True)

# 7. Commit the new data file
subprocess.run(["git", "add", file_name], check=True)
commit_msg = f"Add data update for {date_str} at {time_str}"
subprocess.run(["git", "commit", "-m", commit_msg], check=True)

# 8. Push branch to GitHub (no fetch/rebase needed)
subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)

# 9. Create a pull request back to main using PyGithub
#    Use the GITHUB_TOKEN provided by Actions for authentication:contentReference[oaicite:7]{index=7}.
token = os.environ["GITHUB_TOKEN"]
repo = Github(token).get_repo("AdityaSreevatsaK/CityBikeDataRetrievalAgent")
pr_title = f"Data update for {date_str} at {time_str}"
pr_body = "Automated hourly data update from CityBike API."
repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base="main")

end_time = time.time()
logging.info(f"Script completed in {end_time - start_time:.2f} seconds.")
