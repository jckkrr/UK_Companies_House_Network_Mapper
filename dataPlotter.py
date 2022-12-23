## A script to plot a network map from the dataframes of collated Companies House data, as gatherered in other steps. 
## It is versatile and can be used on all permutations (eg simple dfs and dfs that look to see if two groups are connectable)

import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network
import pyvis
import math 

def makePlot(df, plot_height, colX, colY, centralNodes, circular_images_file):
    
    df = df.fillna('') ### this function doesn't work if it finds a NaN
    
    color_dict = {
        'source': {'name': 'Company', 'r':125,'g':125, 'b': 222, 'a': 1},
        'target': {'name': 'Person','r':0,'g':150, 'b': 100, 'a': 1},
        'highlighted': {'name': 'Highlighted','r':250,'g':150, 'b': 0, 'a': 1},
        'inactive_source': {'name': 'Inactive company','r':170,'g':170, 'b': 222, 'a': 1},
        'inactive_target': {'name': 'Inactive person','r':170,'g':222, 'b': 170, 'a': 1},
    }
    
    circular_images = {}
    for index, row in pd.read_csv(circular_images_file, sep=',') .iterrows():
        circular_images[row['node']] = row['image']
    
    def compileColor(key):
        return f'rgba({color_dict[key]["r"]},{color_dict[key]["g"]},{color_dict[key]["b"]},{color_dict[key]["a"]})'

    g=Network(height=plot_height, width='100%', notebook=True, directed=False)

    def companyNodes(df):
            
        for index, row in df.iterrows():
             
            source, identifier, status, company_status = row[colX], row['company_number'], row['status-tag'], row['company-status']
            
            if company_status == 'Active':
                source_color = compileColor('source')
            else:
                source_color = compileColor('inactive_source')
            
            source_size = 5 + (math.log(row['number_of_persons'], 1.125))
            
            hover_text = f'{source}\n\nID: {str(identifier)}\n{company_status}\n{row["company-type"]}\n{row["company-birth-type"].replace("Incorporated on","Inc:")} {row["company-creation-date"]}'
                        
            g.add_node(source, color=source_color, size=source_size, title=hover_text, font=(f'12 Manrope {source_color}'), identifier=identifier)
                        
    def personsNodes(df):
    
        names = [x for x in df[colY].unique()]
        active_names = [x for x in df.loc[df['status-tag']=='Active', colY].unique()]
        inactive_names = [x for x in names if x not in active_names]
                
        for index, row in df.iterrows():
            
            target_shape = 'dot'
            
            identifier=row['person_idcode']
            
            source, target, edge_text = row[colX], row[colY], row['status-tag']
            
            if target in active_names:
                target_color_node = compileColor('target')
                target_color_text = 'rgba(0,12,0,0.7)'
                
            else:
                target_color_node = compileColor('inactive_target')
                target_color_text = target_color_node
                
            if edge_text == 'Active':
                edge_color = 'rgba(0,150,25,0.75)'
            else:
                edge_color = 'rgba(220,220,220,0.6)'
                
            target_size = 2 + (df.loc[df[colY]==target].shape[0] ** 0.8)
                                
            if target != '':
                g.add_node(target, color=target_color_node, shape = target_shape, size=target_size, title=row[colY] + '\n' + str(identifier) + '\n' + row['status-tag'], font=(f'{10 + (target_size * 0.25)} Manrope {target_color_text}'), identifier=identifier)
                g.add_edge(source, target, weight=5, title=edge_text, color=edge_color)
        
    companyNodes(df)
    personsNodes(df)
    
    ### highlight the central node(s), where applicable
    for node in g.nodes: 
                
        if str(node['identifier']) in centralNodes:
            node['color']='rgba(250,150,0,1)'
            node['font']= f'60 Manrope rgba(22,22,22,1)'
            
        # Make the unscanned empty. 
        label = node['label']    
        if label in df['name'].to_list() and label not in df['company_name'].to_list():
            dfx = df.loc[df.name==label]
            if 1.0 not in dfx['scanned'].to_list():
                node['shape'] = 'circularImage'
                node['image'] = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0D8RJLIfGu9BfAEv3oMYyxiGfkGsGABeSsY6K2Ugy&s'
                                
        # Where there are images for scanned persons, input them
        if label.upper() in [x.upper() for x in circular_images.keys()]:
            if node['shape'] == 'dot': ### to exclude unscanned
                node['shape'] = 'circularImage'
                node['image'] = circular_images[node['label']]
                

    pyvis.options.Layout(improvedLayout=True)    
    g.force_atlas_2based(spring_length=3)
    
    ### Saves a version of the HTML with some style changes
    ### Means you can ignore the file created with g.show
    html = g.generate_html('test.html')
    html = html.replace('border: 1px solid lightgray', 'border: 0px solid lightgray') # removes border that otherwise appears
    html = html.replace('background-color:rgba(200,200,200,0.8)', 'background: linear-gradient(to bottom right, #99ffcc 0%, #ffffcc 100%);') # removes border that otherwise appears
    
    headline = '<span style="font-family: Manrope; font-size: 18px; font-weight:600">Bet365 x JenningsBet</span>'
    subhead = '<span style="font-family: Inter; font-size: 14px; font-weight:200"><b>Data collated from UK Companies House, 19 Dec 2022</b></span>'
    
    def getLegend():
        legend_shell = '<span style="font-family: Inter; font-size:12px">Key: ***REPLACE*** | Unfilled nodes = not scanned for further connections </span>'
        for key in color_dict.keys():
            legend_item = f'<span style="color: rgba({color_dict[key]["r"]},{color_dict[key]["g"]},{color_dict[key]["b"]}, {color_dict[key]["a"]})"> &#9632;</span> {color_dict[key]["name"]}'
            legend_shell = legend_shell.replace('***REPLACE***', legend_item+'***REPLACE***')
        legend = legend_shell.replace('***REPLACE***','')

        return legend
        
    legend = getLegend()

    html = html.replace('<body>', f'<body>\n\n{headline}<br>{subhead}<br>{legend}') # adds title and key
    
    html = html.replace('<style type="text/css">', '<style type="text/css">\n\nbody {font-family: Manrope}') # updates font
    
    fileSlug = 'uk_companies_house_network_mapper_' +  '_'.join(centralNodes)
    Func = open(f'{fileSlug}.html',"w")
    Func.write(html)
    Func.close()
    
    return g