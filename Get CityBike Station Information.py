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

# 1. Fetch Citi Bike station status data
url = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    logging.info("Fetched station status data successfully.")
except requests.exceptions.RequestException as e:
    logging.error(f"Failed to fetch data: {e}")
    data = {}

# 2. Get current date and time in New York timezone
ny_tz = pytz.timezone("America/New_York")
now = datetime.now(ny_tz)
date_str = now.strftime("%d-%m-%Y")
time_str = now.strftime("%H-%M-%S")

# 3. Save data to file
folder_name = date_str
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

file_name = f"{folder_name}/{date_str}_Hour-{time_str}.txt"
with open(file_name, "w") as f:
    f.write(str(data))

# 4. Git configuration
subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)

# 5. Create new branch
branch_name = f"data-update-{date_str}-{time_str}"
subprocess.run(["git", "checkout", "-b", branch_name], check=True)

# 6. Commit and push
subprocess.run(["git", "add", file_name], check=True)
subprocess.run(["git", "commit", "-m", f"Add data update for {date_str} at {time_str}"], check=True)
subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)

# 7. Create PR
token = os.environ["CITYBIKEDATARETRIEVALAGENT_GITHUB_TOKEN"]
repo = Github(token).get_repo("AdityaSreevatsaK/CityBikeDataRetrievalAgent")
repo.create_pull(
    title=f"Data update for {date_str} at {time_str}",
    body="Automated hourly data update.",
    head=branch_name,
    base="main"
)

end_time = time.time()
logging.info(f"Script completed in {end_time - start_time:.2f} seconds.")
