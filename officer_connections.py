## streamlit run "C:\Users\Jack\Documents\Python_projects\uk_companies_house_byAPI\officer_connections.py"


import pandas as pd
from requests import get
import re
import requests
import streamlit as st

### functions

def unpack_json_into_dataframe(v):
    
    df = pd.DataFrame()

    def unpack_json(v, prefix=''):

        if isinstance(v, dict):
            for k, v2 in v.items():
                p2 = "{}['{}']".format(prefix, k)

                px = re.findall("(\w+)",p2)
                px = ':'.join(px).strip()

                unpack_json(v2, px)

        elif isinstance(v, list):
            for i, v2 in enumerate(v):
                p2 = "{}[{}]".format(prefix, i)

                pn = re.findall("\[(.*)\]",p2)[0]
                px = re.sub("\[(.*)\]", f':{pn}', p2)

                unpack_json(v2, px)

        else:
        
            val = repr(v)[1:-1] if repr(v)[0] == "'" and repr(v)[-1] == "'" else repr(v)
            df.loc[0, prefix] = val
                    
    unpack_json(v)
    
    return df

###

def findPersonListings(search_term):
    
    search_url = f"https://api.company-information.service.gov.uk/search/officers"
    params={'q':search_term}
    company_response = requests.get(search_url, auth=(api_key, ''), params=params)
    js = company_response.json() 
            
    df = pd.DataFrame()
    for item in js['items']:
        dfx = unpack_json_into_dataframe(item)
        df = pd.concat([df,dfx])
    df = df.reset_index(drop=True)
    
    try:
        df['officer_id'] = df['links:self'].apply(lambda x: re.findall('/officers/(.*)/appoint',x)[0]) #.group(1)
    except:
        df['officer_id'] = 'X'
    
    first_cols = ['title', 'kind', 'date_of_birth:year', 'date_of_birth:month', 'appointment_count', 'officer_id'] + [x for x in df.columns if 'address' in x]
    ordered_cols = [x for x in first_cols if x in df.columns] + [x for x in df.columns if x not in first_cols]
    df = df[ordered_cols]
    
    return df


#####

def getOfficerAppointments(officer_ids):
    
    df = pd.DataFrame()
    
    for officer_id in officer_ids:

        url = f'https://api.company-information.service.gov.uk/officers/{officer_id}/appointments'
        response = requests.get(url, auth=(api_key, ''))
        js = response.json()


        for item in js['items']:
            dfx = unpack_json_into_dataframe(item)
            df = pd.concat([df,dfx])

        df = df.reset_index(drop=True)

        for key in ['date_of_birth', 'kind', 'is_corporate_officer', 'links']:        
            if key in js.keys():            
                if type(js[key]) == dict:
                    for subkey in js[key].keys():
                        df[f'{key.strip()}:{subkey.strip()}'] = js[key][subkey]
                else:
                    df[key.strip()] = js[key]

        try:
            df['officer_id'] = df['links:self'].apply(lambda x: re.findall('/officers/(.*)/appoint',x)[0]) #.group(1)
        except:
            df['officer_id'] = 'X'
            
            
        for col in ['date_of_birth:year', 'date_of_birth:month']:
            if col in df.columns:
                df[col] = df[col].fillna(0)
                df[col] = df[col].astype(int)

        first_cols = ['name', 'nationality', 'date_of_birth:year', 'date_of_birth:month', 'officer_id', 'officer_role', 'occupation', 'appointed_to:company_name', 'appointed_to:company_number', 'appointed_on',] + [x for x in df.columns if 'address' in x]
        ordered_cols = [x for x in first_cols if x in df.columns] + [x for x in df.columns if x not in first_cols]
        df = df[ordered_cols]
    
    return df


####

def getCompanyPeople(company_numbers):
    
    first_columns = ['name', 'person_type', 'officer_role', 'date_of_birth:year', 'date_of_birth:month', 'nationality', 'country_of_residence', 'occupation']
    df = pd.DataFrame(columns=first_columns)
    
    for company_number in company_numbers:
        
        st.write(company_number)
        
        dfC = pd.DataFrame()
        
        company_name = None
        company_name_url = f"https://api.companieshouse.gov.uk/company/{company_number}"
        company_name_response = requests.get(company_name_url, auth=(api_key, ''))
        company_name_js = company_name_response.json()  
        if 'company_name' in company_name_js.keys():
            company_name = company_name_js['company_name']
        
        
        ### Get Officers ###

        company_url = f"https://api.companieshouse.gov.uk/company/{company_number}/officers"
        company_response = requests.get(company_url, auth=(api_key, ''))        
        js = company_response.json()

        if 'items' in js.keys():
            for item in js['items']:
                dfx = unpack_json_into_dataframe(item)
                dfx['person_type'] = 'Officer'
                dfC = pd.concat([dfC, dfx])


        ### Get PSCS ###

        company_url = f"https://api.companieshouse.gov.uk/company/{company_number}/persons-with-significant-control"
        company_response = requests.get(company_url, auth=(api_key, ''))
        js = company_response.json()
        
        if 'items' in js.keys():
            for item in js['items']:
                dfx = unpack_json_into_dataframe(item)
                dfx['person_type'] = 'PSC'
                dfC = pd.concat([dfC, dfx])
                
        dfC['company_number'] = company_number
        dfC['company_name'] = company_name
        df = pd.concat([df, dfC])
    
    first_columns = ['name', 'person_type', 'officer_role', 'date_of_birth:year', 'date_of_birth:month', 'nationality', 'country_of_residence', 'company_number', 'company_name']
    ordered_columns = [x for x in first_columns if x in df.columns] + [x for x in df.columns if x not in first_columns]    
    df = df[ordered_columns]
    
    return df


##################################################


st.write('Constituent Investigative Analytics Studio')

st.write('# UK COMPANIES HOUSE OFFICER CONNECTIONS CHECKER #####')

api_key = st.text_input('Please enter API key')
#api_key = ''

if len(api_key) > 10:

    search_term = st.text_input('Who would like to search for?', 'lydia alexandra gordon')

    if len(search_term) > 0:

        dfSEARCH = findPersonListings(search_term)
        st.dataframe(dfSEARCH)

        selected_options = st.multiselect(
            'By row number, select which records that you would like to include in search:',
            [x for x in range(0, dfSEARCH.shape[0])], [0])

        selected_options_byname = dfSEARCH.loc[selected_options, 'title'].to_list()

        st.write('Selected:', ', '.join(selected_options_byname))

        proceed = st.radio('Ready to go?', ['yes', 'no'], horizontal=True)

        if proceed == 'yes':

            st.write('Getting data ...')

            officer_ids = dfSEARCH.loc[selected_options, 'officer_id'].to_list()

            #st.write(officer_ids)

            dfAPPOINTMENTS = getOfficerAppointments(officer_ids)
            st.dataframe(dfAPPOINTMENTS)

            company_numbers = dfAPPOINTMENTS['appointed_to:company_number']

            if len(company_numbers) > 0:

                st.write('Searching for who is involved with these companies:')

                dfCOMPANYPEOPLE = getCompanyPeople(company_numbers)

                all_individuals = list(dfCOMPANYPEOPLE['name'].unique())

                st.write('These are the people connected to the person(s) who searched for:')
                
                ############### VISUALISE ############################
                
                import plotly.graph_objects as go
                import networkx as nx
                import streamlit.components.v1 as components
                import pyvis
                
                #G = nx.from_pandas_edgelist(dfCOMPANYPEOPLE, 'name', 'company_name', None)
                
                G = nx.Graph()
                for index, row in df.iterrows():
                    node_name, node_company = row['name'], row['nationality']
                    G.add_node(node_name, color='red')
                    G.add_node(node_company, color='green')
                    G.add_edge(node_name, node_company)

                fig = pyvis.network.Network(width=1000, directed=False)

                fig.from_nx(G)

                path = '/tmp'
                fig.save_graph(f'temp.html')
                HtmlFile = open(f'temp.html', 'r', encoding='utf-8')

                components.html(HtmlFile.read(), height=550)
                
                st.write(G.nodes)
                #################################
                
                st.write('More details:')
                st.dataframe(dfCOMPANYPEOPLE)
                
st.write('')
st.write('')
st.write('&#11041; More tools at www.constituent.au')