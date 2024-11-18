#!/usr/bin/env python3
from flask import Flask, jsonify
import semprpy as sempr
from semprpy import rdf, rdfs, rete
import json
import re
from datetime import datetime, timedelta, date
import weather/weather
import read
from flask import request
from flask import g
import os
import weather/weat1
import pandas as pd
import glob


app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_wmes():

    global core

    core = sempr.Core("db")
    core.loadPlugins()



    def verbose(msg):
        return msg
    
    file = open("rules/agronw_eval.rules", "r")
    content = file.read()
    core.addRules(verbose(content))
    file.close()

    core.performInference()
    
    def extract_area_code_from_file(file_path):
        with open(file_path) as file:
            data = json.load(file)
        
        area_code = None
        components = data.get("value0", {}).get("ptr_wrapper", {}).get("data", {}).get("components", [])
        
        for component in components:
            key_data = component.get("key", {}).get("ptr_wrapper", {}).get("data", {}).get("map", [])
            for entry in key_data:
                if entry.get("key") == "agnw:Areacode":
                    area_code = entry.get("value", {}).get("strValue")
                    return area_code
        return area_code
    def extract_area_codes_from_folder(folder_path):
        area_codes = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                area_code = extract_area_code_from_file(file_path)
                area_codes.append(area_code)
        return area_codes

# Specify the folder containing the JSON files
    folder_path = 'db/'
    area_codes = extract_area_codes_from_folder(folder_path)
    given_date = date.today()
    given_date_str = given_date.strftime('%d.%m.%Y')

    for i in area_codes:

        weather.station_example(str(i), str(given_date_str))
        weat1.station_example(str(i))
        read.read_weather()
        
        df = pd.read_csv('input_weather_tm.csv')
        
        given_date = given_date.strftime("%Y-%m-%d")
        
        given_date = datetime.strptime(given_date, "%Y-%m-%d")
        
        
        three_days_ago = given_date - timedelta(days=4)
        three_days_ago = three_days_ago.strftime("%Y-%m-%d")
        seven_days_later = given_date + timedelta(days=7)
        seven_days_later = seven_days_later .strftime("%Y-%m-%d")

        start_date = three_days_ago
        
        end_date = seven_days_later
        

        mask = (df['date_only'] >= str(start_date)) & (df['date_only'] <= str(end_date))

        filtered_df = df.loc[mask]
        filtered_df = filtered_df.drop(columns=['Unnamed: 0'])
        filtered_df = filtered_df.reset_index()
        filtered_df = filtered_df.drop(columns=['index'])
        

        WeatherData_entity = {}
        for j in range(len(filtered_df)):

            WeatherData_entity[f'WeatherData_{j}'] = sempr.Entity()

            tpm1 = sempr.TriplePropertyMap()
            tpm1["rdf:type"] = "agnw:WeatherData", True
            tpm1["agnw:Areacode"] = str(i)
            tpm1["agnw:WDate"] = str(filtered_df['date_only'][j])
            tpm1["agnw:Temp"] = filtered_df['temperature_air_mean_200'][j]
            tpm1["agnw:Rain"] = filtered_df['precipitation_height'][j]
            tpm1["agnw:Sunshine"] = filtered_df['sunshine_duration'][j]

            WeatherData_entity[f'WeatherData_{j}'].addComponent(tpm1)
            core.addEntity(WeatherData_entity[f'WeatherData_{j}'])

    
    # Create entity and component for date
    given_date = given_date.strftime("%Y-%m-%d")
    
    Date = sempr.Entity()
    tpm2 = sempr.TriplePropertyMap()
    tpm2["rdf:type"] = "agnw:Date", True

    tpm2["agnw:Today"] = str(given_date)

    Date.addComponent(tpm2)
    core.addEntity(Date)

    print("++++++++++++++++++++++++++++++")
    core.performInference()

    # Specify the folder name
    folder_name = 'db/'

    # Get a list of all files that start with 'Entity'
    files = glob.glob(os.path.join(folder_name, 'Entity*'))

    # Loop through the list and delete each file
    for file in files:
        os.remove(file)

    

    state = core.reasoner.inferenceState
    wmes = state.getWMEs()
    wmes_global = wmes
    wmes1 = []
    for i in wmes:
        mystring = str(i)
        mystring = re.sub("[()]", "",mystring)

        pattern = r'<agnw:Fertilizable>|<agnw:FertOption>|<agnw:FertType>|<agnw:FertQty>|<agnw:CloverRateRank>|<agnw:Harvestable>|<agnw:RcomeHarvesting>|<agnw:ManagementOption>|<agnw:RecomMeasure>'
        exist= re.findall(pattern, mystring)
        if len(exist) > 0:

            mystring = re.sub(r'>|<|agnw:|sempr:', '', mystring)
            text = mystring.split()
            for t in range(len(text)):
                if t == 0:
                    mystring = text[t]
                else:
                    mystring = mystring + " " + text[t]
            
            wmes1.append(mystring)
            

    with open('wmes1.json', 'w') as file:
            
            json.dump(wmes1, file)
    return jsonify(wmes1)

    



@app.route('/fwmes', methods=['GET', 'POST'])
def fwmes():

    state = core.reasoner.inferenceState
    wmes = state.getWMEs()
    wmes_global = wmes
    wmes1 = []
    for i in wmes:
        mystring = str(i)
        mystring = re.sub("[()]", "",mystring)
        wmes1.append(mystring)

    with open('wmes.json', 'w') as file:
            
            json.dump(wmes1, file)
    

    return jsonify(wmes1)
    

@app.route('/explain', methods=['GET', 'POST'])
def explain():

    row = request.form.get('row')
    state = core.reasoner.inferenceState
    wmes = state.getWMEs()

    
    for i in range(len(wmes)):

        strig_to_find = re.sub("[()]", "", str(wmes[i]))
        pattern = r'<agnw:Fertilizable>|<agnw:FertOption>|<agnw:FertType>|<agnw:FertQty>|<agnw:CloverRateRank>|<agnw:Harvestable>|<agnw:RcomeHarvesting>|<agnw:HarvestReason>|<agnw:ManagementOption>|<agnw:RecomMeasure>'
        exist= re.findall(pattern, strig_to_find)
        if len(exist) > 0:

            strig_to_find = re.sub(r'>|<|agnw:|sempr:', '', strig_to_find)
            text = strig_to_find.split()
            for t in range(len(text)):
                if t == 0:
                    strig_to_find = text[t]
                else:
                    strig_to_find = strig_to_find + " " + text[t]
                
            

            if row == strig_to_find:

                print("row: ", row)
                print("strig_to_find: ", strig_to_find)
                print("wmes[i]: ", wmes[i])

                v = rete.ExplanationToJSONVisitor()
                state.traverseExplanation(wmes[i], v)

                with open('test_result.json', 'w+') as f:
                    json.dump(v.json(), f, indent=4)

                break

    
    return jsonify(v.json())


if __name__ == '__main__':
    app.run(port=5000, debug=True)