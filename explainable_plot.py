import json
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.offline as py
from collections import Counter
import os
import glob
from datetime import date, timedelta



ref_dict = {
    "wmes": ["Harvestable Hay", "Harvestable Silo", "HarvestReason Grass height", "HarvestReason Crude fiber", "ManagementOption TineWeeding", "Fertilizable true", "CloverRateRank medium", "CloverRateRank high", "CloverRateRank low", "HarvestReason Growth stage grass 2"],
    "descriptions":["Harvesting option is hay ", "Harvesting option is silo ", "Harvest reason grass height ", "Harvest reason is crude fiber ", "Tine Weeding is a management option ", "Field can be fertilized ", "Clover rate is medium ", "Clover rate is high ", "Clover rate is low ", "Harvest reason is growth stage grass 2 "]
}

ref_df = pd.DataFrame(ref_dict)

def plot_sunburst(row):
        
        row = re.sub(r'Field_\d+ ', '', row)
        row = re.sub(r'"', '', row)
        print("row:", row)
        result_list = ref_df['descriptions'].where( ref_df['wmes'] == row).dropna().tolist()
        print("result_list:", result_list)
        df = pd.read_json("test_result.json")
        print("Dataframe:")
        print(df.columns)
        description = []
        variables = []

        for elements in df['value']:
            
            if isinstance(elements, dict):
                description.append(elements["description"])

                if "variables" in elements:  # Check if 'variables' key is in the dictionary
                    variables.append(elements["variables"])
                else:
                    variables.append(None)
            else:
                description.append("")
                variables.append(None)
            

        df['description'] = description
        df['variables'] = variables
        df.drop(['value', 'type'], axis=1, inplace=True)

        df.to_csv('output.csv', index=False)

        for i in range(len(df)):
            if type(df['based_on'][i]) is not list:
                df.at[i, 'based_on'] = []

        deletable_ids = []
        for i in range(len(df)):
            if len(df["description"][i]) == 0:
                for j in range(len(df)):
                    if df["id"][i] in df["based_on"][j]:
                        print("hello")
                        df.at[j, "based_on"].remove(df.at[i, "id"])
                        df.at[j, "based_on"] = list(set(df.at[j, "based_on"] + df.at[i, "based_on"]))
                        deletable_ids.append(df.at[i, "id"])

        
        df = df[df['description'].notnull() & (df['description'] != '')]
        df.reset_index(drop=True, inplace=True)
        
        df.to_csv('output1.csv', index=False)

        for i in range(len(df)):
             if type(df['variables'][i]) is dict:
                  targ = df['variables'][i]
                  keys = list(targ.keys())
                  for key in keys:
                       if key == 'avgRain':
                            df['description'][i] = re.sub(key, targ[key], df['description'][i])
        
        df.to_csv('output11.csv', index=False)
        
        
        parent = [""]
        child = []
        child.append(result_list[0])


        def recursive_child(targ_index, parent, child):
            if len(df['based_on'][targ_index]) >0:
                        print("targ_index:", targ_index)
                        for j in range(len(df['based_on'][targ_index])):
                            parent.append(df['description'][targ_index])
                            for k in range(len(df)):
                                if  df['based_on'][targ_index][j] == df['id'][k]:
                                    print("based_on:", df['based_on'][targ_index][j])
                                    print
                                    child.append(df['description'][k])
                                    recursive_child(k, parent, child)
                                
            else:
                    return parent, child
                
        for i in range(len(df)):
            if df['description'][i] in result_list:
                for j in range(len(df['based_on'][i])):
                    
                    parent.append(df['description'][i])
                    for k in range(len(df)):
                        if  df['based_on'][i][j] == df['id'][k]:
                            print("based_on:", df['based_on'][i][j])
                            
                            child.append(df['description'][k])
                            recursive_child(k, parent, child)
                        
        
        
        
        print("len of parent:", len(parent))
        print("Parent:", parent)
        print("len of child:", len(child))
        print("Child:", child) 

        data = {}
        data["character"] = parent
        data["parent"] = child
        data = dict(
            character=child,
            parent=parent,
            )
        # Convert the dictionary to a DataFrame
        df34 = pd.DataFrame(data)
        
        # Save the DataFrame as a CSV file
        df34.drop_duplicates(inplace=True)

        df_filtered = df34[~df34['character'].isin(['Asserted. No explanation, that is just how it is.', 'unconditional/true', 'date:diff', 'date:month', 'noValue'])]
        df_filtered = df_filtered[~df_filtered['character'].str.contains(' LE | GE | LT | GT ', regex=True)]
        df_filtered = df_filtered[~df_filtered['character'].str.contains(r'/.*=|\(.*=', regex=True)]
        #df34 = df34.loc[~df34['character'].isin(['Asserted. No explanation, that is just how it is', 'unconditional/true'])]

        
        today = date.today()
        two_days_before = today - timedelta(days=2)
        three_days_after = today + timedelta(days=3)
        seven_days_after = today + timedelta(days=7)
        # Extract the current month
        current_month = today.month
        print("today:", today)
        print("two_days_before:", two_days_before)

        for i in range(len(df_filtered)):
            if re.search(r"Average rainfall in the next 7 days ", df_filtered.iloc[i]['parent']):
                df_filtered.iloc[i]['character'] = re.sub("wdate", str(seven_days_after), df_filtered.iloc[i]['character'])
                df_filtered.iloc[i]['character'] = re.sub("today", str(today), df_filtered.iloc[i]['character'])
                for j in range(i + 1, len(df_filtered)):
                    if re.search(r"Calculate average rainfall from {today} to {wdate}", df_filtered.iloc[j]['parent']):
                         df_filtered.iloc[j]['parent'] = re.sub("wdate", str(seven_days_after), df_filtered.iloc[j]['parent'])
                         df_filtered.iloc[j]['parent'] = re.sub("today", str(today), df_filtered.iloc[j]['parent'])
                    else:
                        break

            elif re.search(r"Average rainfall in the next 3 days ", df_filtered.iloc[i]['parent']):
                df_filtered.iloc[i]['character'] = re.sub("wdate", str(three_days_after), df_filtered.iloc[i]['character'])
                df_filtered.iloc[i]['character'] = re.sub("today", str(today), df_filtered.iloc[i]['character'])
                for j in range(i + 1, len(df_filtered)):
                    if re.search(r"Calculate average rainfall from the day {today} to {wdate}", df_filtered.iloc[j]['parent']):
                         df_filtered.iloc[j]['parent'] = re.sub("wdate", str(three_days_after), df_filtered.iloc[j]['parent'])
                         df_filtered.iloc[j]['parent'] = re.sub("today", str(today), df_filtered.iloc[j]['parent'])
                    else:
                        break

            elif re.search(r"Average rainfall in the last 2 days was ", df_filtered.iloc[i]['parent']):
                df_filtered.iloc[i]['character'] = re.sub("wdate", str(two_days_before), df_filtered.iloc[i]['character'])
                df_filtered.iloc[i]['character'] = re.sub("today", str(today), df_filtered.iloc[i]['character'])
                for j in range(i + 1, len(df_filtered)):
                    if re.search(r"Calculate average rainfall from {wdate} to {today}", df_filtered.iloc[j]['parent']):
                         df_filtered.iloc[j]['parent'] = re.sub("wdate", str(two_days_before), df_filtered.iloc[j]['parent'])
                         df_filtered.iloc[j]['parent'] = re.sub("today", str(today), df_filtered.iloc[j]['parent'])
                    else:
                        break
            elif re.search(r"Month {month} is between ", df_filtered.iloc[i]['character']):
                df_filtered.iloc[i]['character'] = re.sub("month", str(current_month), df_filtered.iloc[i]['character'])
                for j in range(i + 1, len(df_filtered)):
                    if re.search(r"Month {month} is between ", df_filtered.iloc[j]['parent']):
                        df_filtered.iloc[j]['parent'] = re.sub("month", str(current_month), df_filtered.iloc[j]['parent'])
                    else:
                        break
                 
                 
        

        for i in range(len(df_filtered)):
            for j in range(i + 1, len(df_filtered)):
                if df_filtered.iloc[i]['character'] == df_filtered.iloc[j]['character']:
                    df_filtered.iloc[j]['character'] = " " + df_filtered.iloc[j]['character']

        df_filtered.to_csv('data545.csv', index=False)

        character = df_filtered['character']
        parent = df_filtered['parent']
        data = {
            ' ': character,
            'Supports ': parent
        }

        fig = px.sunburst(
            data,
            names=' ',
            parents='Supports ',
            
        )
        # Save the figure as an HTML file.
        py.plot(fig, filename='sunburst_plot.html', auto_open=False)
       