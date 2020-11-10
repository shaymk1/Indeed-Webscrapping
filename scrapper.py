from datetime import datetime
# import pandas as pd
import csv
import time
import requests
from bs4 import BeautifulSoup

time.sleep(5)


# generating url position and funtion

def get_url(position, location):
    template = 'https://www.indeed.co.za/jobs?q={}&l={}'
    position = position.replace(" ", "+")
    location = location.replace(" ", " +")
    url = template.format(position, location)
    return url


"""Extract job data from a single record"""


def get_record(job_card):
    job_title = job_card.h2.a  # because they were nested in h2 and an a tag
    company = job_card.find('span', 'company').text.strip()
    job_location = job_card.find('div', 'recJobLoc').get('data-rc-loc')  # to be more specific, we use data-rc-loc
    post_date = job_card.find('span', 'date').text
    today = datetime.today().strftime('%Y-%m-%d')
    summary = job_card.find('div', 'summary').text.strip().replace('\n', ' ')
    job_url = 'https://www.indeed.co.za' + job_card.h2.a.get('href')

    salary_tag = job_card.find('span', 'salaryText')
    # this does not exist for every listing, so we use handle exception with if

    if salary_tag:
        salary = salary_tag.text.strip()
    else:
        salary = ''

    record = (job_title, company, job_location, post_date, today, summary, salary, job_url)
    return record


"""Run the main program routine"""


def main(position, location):
    records = []
    url = get_url(position, location)
    # extract the job data
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', 'jobsearch-SerpJobCard')
        for job_card in job_cards:
            record = get_record(job_card)
            records.append(record)
        try:
            # to get to the next page, we use soup.find 'a' with aria -label :next
            # href will tell us that we have reached the end of the page if we cant find it
            url = 'https://www.indeed.co.za' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:
            break

    # save the job data
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'Salary', 'JobUrl'])
        writer.writerows(records)

    # or save the job data to using pandas
    # records = pd.DataFrame(records)
    # records.columns = ['JobTitle', 'Company', 'Location', ' Summary', 'PostDate', 'ExtractDate', 'Salary', 'JobUrl']
    # records.to_csv('records.csv', index=False)


# run the main program
main('web developer', 'south africa')
