import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from .dataset.skills import (
    business_skills,
    specialty_skills,
    law_skills,
    health_skills,
    education_skills,
    information_technology_skills,
    engineering_skills,
)

def scrape_skills_from_page(url):

    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'class': 'l-table'})
        
        if table:
            skills_data = []
            
            rows = table.find('tbody').find_all('tr')
            
            for row in rows:
                columns = row.find_all('td')
                
                if len(columns) > 1:
                    # extract the relevant columns (the first column is "Categories" and the second is "Rich Skill Descriptor")
                    category = columns[0].get_text(strip=True)
                    skill_descriptor = columns[1].get_text(strip=True)
                    
                    skills_data.append({
                        'category': category,
                        'rich_skill_descriptor': skill_descriptor
                    })
                    
            return skills_data
        else:
            print(f"Table not found on page: {url}")
            return None
    else:
        print(f"Failed to fetch the page: {url}, Status Code: {response.status_code}")
        return None

def get_total_pages(soup):
    """Extract total number of pages from pagination element."""
    pagination = soup.find('div', {'class': 'm-pagination'})
    if pagination:
        page_info = pagination.find('p', {'class': 'm-pagination-x-total'}).get_text(strip=True)
        total_pages = int(page_info.split(" of ")[1])  # extract total number of pages
        return total_pages
    return 1  # default to 1 if pagination not found

def scrape_all_pages(base_url):
    current_page = 1
    all_skills = []
    
    while True:
        page_url = f"{base_url}?page={current_page}"
        print(f"Scraping page {current_page}: {page_url}")
        
        response = requests.get(page_url)
        if response.status_code != 200:
            print(f"Failed to fetch page {current_page}, stopping.")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if current_page == 1:
            total_pages = get_total_pages(soup)
            print(f"Total pages found: {total_pages}")
        
        skills = scrape_skills_from_page(page_url)
        if skills:
            all_skills.extend(skills)
        else:
            print(f"No skills found on page {current_page}.")
        
        if current_page >= total_pages:
            break
        
        current_page += 1
        
        time.sleep(5)

    return all_skills


def main():

    skill_types = [
        business_skills,
        specialty_skills,
        law_skills,
        health_skills,
        education_skills,
        information_technology_skills,
        engineering_skills
    ]

    urls_list = [url for skill_type in skill_types for sublist in skill_type.values() for url in sublist]

    for url in urls_list:
        skills_data = scrape_all_pages(url)

        skills_df = pd.DataFrame.from_dict(skills_data, orient='index').transpose()

        print(skills_df)


