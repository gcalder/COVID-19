# COVID-19

## Overview
This workflow is designed to fulfil two requirements:

  1) Scrape data from the Scottish Government's website on a daily basis and automatically generate a daily report.
  2) Produce a bi-weekly report for the Scottish Advisory Group on COVID-19.

*Daily Report*
We scrape Health Protection Scotland (HPS) COVID-19 data from the Scottish Government's website, append today's data to yesterday's and perform an automated analysis of key epidemiological metrics and trends. Originally, the entire process (scraping, analysis and plotting) was done in python. Later versions of the report use R for plotting, and we cross-check the numerical results produced by both scripts for quality assurance.

*SAG Report*
This report is distributed twice a week, and uses the same raw HPS data as the daily report, as well as data from the National Records of Scotland (NRS).

## Usage
You will need to have python 3.0, a python interpreter, R and RStudio installed. The python code was developed in jupyter notebooks (.ipynb), but will also run as .py file.

*Daily Report*

  1) Run the 'COVID-19_DailyScraper_Basic' python script
  2) Run the 'render_reports_wkgr' R script
  
Following these steps should result in 3 files being produced in the working directory: .html, .pdf and .txt 
In a production environment, the .txt file is passed to the body of an email, to which the .html and .pdf files are attached.
In the interests of security, specific details of how both reports are distributed are delibarately omitted here.

*SAG Report*

Make sure that the raw data from HPS and NRS are in place.

## Contributing
* To contribute, please create a branch and submit a pull request to master. Please do not push directly to master.
* Raise issues through Github and link them to PRs once submitted.
