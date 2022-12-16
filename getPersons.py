### A script to get all the officers associated with a company in the UK's Companies House registry
### Requires having the id number of the company in question, which can be found on their CH webpage 

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup, Tag

def getPersons(company_number):
    
    def getTab(tab):
    
        df = pd.DataFrame(columns=['company_number', 'company_name', 'person_type'])

        url = f'https://find-and-update.company-information.service.gov.uk/company/{company_number}/{tab}'    
        page = requests.get(url)                                
        soup = BeautifulSoup(page.content, 'html.parser')
        
        company_name = re.search('([A-Z0-9 ()\'&.]+) (pe)', str(soup.title.text).replace("’","'"))
        if company_name != None:
            company_name = re.sub(' people','', company_name.group(1))
        
        appointments_list = soup.find('div', {'class':'appointments-list'})

        for tag in appointments_list.find_all():    
            if len(tag.attrs.keys()) == 1 and 'class' in tag.attrs.keys() and type(tag.attrs['class']) == list and len(tag.attrs['class']) == 1:
                    res = re.search('appointment-(\d+)', tag.attrs['class'][0])
                    
                    if bool(res):
                        person_number = re.search('(\d+)', res.group(1)).group(1)                    
                        person_info = appointments_list.find('div', {'class': f'appointment-{person_number}'})
                        
                        nr = df.shape[0]+1
                        df.loc[nr, ['company_number', 'company_name', 'person_type']] = company_number, company_name, 'psc' if tab == 'persons-with-significant-control' else tab

                        for person_info_tag in person_info.find_all():
                        
                            if 'id' in person_info_tag.attrs.keys():

                                if len(person_info_tag.attrs) == 1 or 'officer-status-tag' in person_info_tag['id']:
                                    idtype = person_info_tag['id']
                                    val = appointments_list.find(id=idtype) if appointments_list.find(id=idtype) == None else appointments_list.find(id=idtype).text.strip()
                                     
                                    if 'officer-name' in person_info_tag['id']: ## not seen on psc page
                                                                  
                                        person_link = person_info_tag.a['href']
                        
                                        person_idcode = re.search('\/officers\/([\w-]+)\/appointments', person_link)
                                        if person_idcode != None:
                                            person_idcode = person_idcode.group(1)

                                        df.loc[nr, ['person_idcode', 'person_link']] = person_idcode, person_link

                                elif 'class' in person_info_tag.attrs.keys() and person_info_tag.attrs['class'][0] == 'data':
                                    idtype = person_info_tag['id']
                                    val = person_info_tag.text.strip()

                                key = re.sub('-(\d+)', '', idtype).replace('officer-','').replace('psc-','')
                                df.loc[nr, key] = val

        df['company_number'] = company_number
        df['company_name'] = company_name
        
        return df

    df1 = getTab('officers')
    df2 = getTab('persons-with-significant-control')
    
    df = pd.concat([df1,df2])
    df = df.reset_index(drop=True)

    return df
 
                            
################################

### This script allows you to compile info from the pages of multiple companies.
### Just feed a list into the function

def getManyCompanies(list_of_ids):

    df = pd.DataFrame()
    
    ###
    
    for idcode in list_of_ids:

        print(idcode, end='\t')

        try:
            dfx = getPersons(idcode)
        except:
            dfx = getPersons(idcode)

        df = pd.concat([df,dfx])

        print(df.shape)

    df = df.reset_index(drop=True)
    df['company_display'] = df['company_name'].str.upper()
    df['person_display'] = df['name'].str.upper()
    df['name-hover'] = df['status-tag'] + ' : ' +  df['name'] 
    
    return df

######