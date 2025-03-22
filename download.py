import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
url = "https://www.meritechcapital.com/benchmarking/comps-table"
driver.get(url)

# Let JavaScript load
time.sleep(5)

# Parse the page
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Find table
table = soup.find("table")

rm_headers = ["% Price Px.", "% YoY Growth", "% LTM Margins"]

# Extract headers
headers = [th.get_text(strip=True) for th in table.find_all("th")]

# 1. Find start of 'Mean' and 'Median'
mean_index = headers.index("Mean")
median_index = headers.index("Median")

# 2. Split the raw list
main_headers = headers[:26]  # First 26 columns are standard (confirmed from example)
sub_headers = headers[26:mean_index]  # All the sub-columns
mean_row = headers[mean_index:median_index]
median_row = headers[median_index:]

# 3. Map headers with sub-columns
prefix_map = {
    "% Price Px.": ["3-Mo", "12-Mo"],
    "% YoY Growth": ["Implied ARR", "LTM Revenue", "NTM Revenue"],
    "% LTM Margins": ["GM", "S&M", "R&D", "G&A", "OpEx", "Operating Income", "FCF"]
}

# 4. Construct final header row
final_headers = []
rows = []
for col in main_headers:
    if col in prefix_map:
        for sub in prefix_map[col]:
            final_headers.append(f"{col} - {sub}")
    else:
        final_headers.append(col)

for tr in table.find_all("tr")[1:]:  # Skip header row
    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
    if not cells:
        continue  # Skip empty rows

    # Check if the row is Mean or Median
    if cells[0] == "Mean":
        mean_row = cells
        continue
    elif cells[0] == "Median":
        median_row = cells
        continue

    rows.append(cells)

# 取得今天日期
today = datetime.today().strftime('%Y-%m-%d')
filename = f"data/meritech_comps_{today}.csv"

# Save to CSV with date in filename
with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    
    # Write headers
    writer.writerow(final_headers)

    # Write company rows
    writer.writerows(rows)

    # Write Mean and Median rows
    if mean_row:
        writer.writerow(["Mean"] + mean_row[1:])
    if median_row:
        writer.writerow(["Median"] + median_row[1:])

print(f"✅ Saved table with Mean/Median to {filename}")