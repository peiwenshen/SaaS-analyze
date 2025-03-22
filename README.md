# 📊 SaaS Analyze - Meritech Index Tracker

This project automatically scrapes and tracks daily SaaS company metrics from the [Meritech Capital Comps](https://www.meritechcapital.com/benchmarking/comps-table) page.

Each day, a GitHub Action runs a script that:
- Scrapes updated valuation data from the site using Selenium + BeautifulSoup
- Saves the data as a timestamped CSV (`data/meritech_comps_YYYY-MM-DD.csv`)
- (Optional) Generates a regression plot and stores it under `plots/`
- Commits and pushes the new data to this repo