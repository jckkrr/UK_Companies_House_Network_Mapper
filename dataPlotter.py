## A script to plot the dataframes of info gatherered in other steps as a network map
## Versatile: can be used on all permutations (eg simple dfs and dfs that look to see if two groups are connectable)

import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network
import pyvis

def makePlot(df, colX, colY, centralNodes):
    
    df = df.fillna('') ### this function doesn't work if it finds a NaN

    g=Network(height='900px', width='100%', notebook=True, directed=False)

    def companyNodes(df):
            
        for index, row in df.iterrows():
            
            source, identifier = row[colX], row['company_number']
            
            source_color = 'rgba(125,125,222,0.5)'
            source_size = 10  + (df.loc[df[colX]==source].shape[0] * 0.5)
            g.add_node(source, color=source_color, size=source_size, title=source, font=(f'12 Manrope {source_color}'), identifier=identifier)
            
    def personsNodes(df):
    
        names = [x for x in df[colY].unique()]
        active_names = [x for x in df.loc[df['status-tag']=='Active', colY].unique()]
        inactive_names = [x for x in names if x not in active_names]
                
        for index, row in df.iterrows():

            source, target, edge_text = row[colX], row[colY], row['status-tag']
                        
            if target in active_names:
                target_color_node = 'rgba(0,150,25,0.7)'
                target_color_text = 'rgba(0,12,0,0.7)'
                
            else:
                target_color_node = 'rgba(200,220,220,0.4)'
                target_color_text = target_color_node
                
            if edge_text == 'Active':
                edge_color = 'rgba(0,150,25,0.05)'
            else:
                edge_color = 'rgba(200,220,220,0.05)'
                
            target_size = 2 + (df.loc[df[colY]==target].shape[0] ** 0.8)
        
            target = target.replace('DIERDRE', 'DEIRDRE')
            
            if target != '':
                g.add_node(target, color=target_color_node, size=target_size, title=row[colY], font=(f'{10 + (target_size * 0.25)} Manrope {target_color_text}'), identifier=row['person_idcode'])
                g.add_edge(source, target, weight=5, title=edge_text, color=target_color_node)
        
    companyNodes(df)
    personsNodes(df)
    
    ### highlight the central node(s), where applicable
    for node in g.nodes:        
        if node['identifier'] in centralNodes:
            node['color']='rgba(250,150,0,1)'
            node['font']= f'12 Manrope rgba(22,22,22,1)'
    
    pyvis.options.Layout(improvedLayout=True)

    return g