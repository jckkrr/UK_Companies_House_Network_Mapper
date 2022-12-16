### A script to harvest all the appointments of an individual from the UK's Companies House registry
### Note that this requires having the id number of the preson in question, which can be found on their CH webpage 
### We have found that some people are spread across multiple id numbers, so what this script returns should be taken as a guide only.

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup, Tag

def getOfficerAppointments(personal_id):
    
    df = pd.DataFrame(columns=['officer_name', 'date_of_birth', 'officer_id'])
        
    url = f'https://find-and-update.company-information.service.gov.uk/officers/{personal_id}/appointments'
    page = requests.get(url)                                
    soup = BeautifulSoup(page.content, 'html.parser')

    pages = soup.find('ul', {'class': 'pager'})
    if bool(pages):
        pps = [x.text.strip() for x in pages.find_all('li')]
        pps = [int(x) for x in pps if x.isnumeric()]
    else:
        pps=[1]

    def getPage(pp, pp1_soup):
        
        if pp == 1:
            soup = pp1_soup
        else:
            url = f'https://find-and-update.company-information.service.gov.uk/officers/{personal_id}/appointments?page={pp}'
            page = requests.get(url)                                
            soup = BeautifulSoup(page.content, 'html.parser')
        
        officer_name = soup.find('h1', {'id':'officer-name'}).text
        
        appointments = soup.find('div', {'class': 'appointments'})
        
        date_of_birth = appointments.find('dd', {'id':'officer-date-of-birth-value'}).text if bool(appointments.find('dd', {'id':'officer-date-of-birth-value'})) else None
    
        appointments_list  = appointments.find('div', {'class': 'appointments-list'})

        for tag in appointments_list.find_all():
            if len(tag.attrs.keys()) == 1 and 'class' in tag.attrs.keys():            
                res = re.search('appointment-(\d+)', str(tag.attrs['class']))
                if bool(res):

                    nr = df.shape[0] + 1

                    appointment_number = res.group(1)
                    for subtag in tag.find_all():
                        if 'id' in subtag.attrs.keys():
                            key = re.sub('(-*)(\d+)','',subtag.attrs['id']).strip()
                            val = subtag.text.replace('\n','').replace('\t','').replace('  ','').strip()
                            df.loc[nr, key] = val

                            if 'company-name' in key:
                                href_slug = subtag.a['href']
                                href = 'https://find-and-update.company-information.service.gov.uk' + href_slug
                                company_id = href_slug.split('/')[-1]
                                df.loc[nr, ['company_id', 'href']] = company_id, href
                                
        df['officer_name'] = officer_name
        df['date_of_birth'] = date_of_birth
        df['officer_id'] = personal_id
         
    for pp in pps:
        getPage(pp, soup) 

    return df