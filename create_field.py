import pandas as pd
import numpy as np
import json

def add_field(var, length):

        df = pd.read_csv('Keys_Classified_by_Type.csv')
        map = []


        type_0 = list(df['0'])
        type_1 = list(df['1'])
        type_2 = list(df['2'])
        type_3 = list(df['3'])

        data = {
                                            "base": {},
                                            "wkt": "POLYGON (())"
                                        }

        for i in range(len(var)):

            xt = {  "key": "",
                "value": {
                            "type": 0,
                            "strValue": "",
                            "fltValue": 0.0,
                            "intValue": 0}
            }
            
            if var[i][0] == 'coordinates':
                temp = []
                count = 0
                for cord in var[i][1]:
                    if count == 0:
                        string = f"POLYGON (({cord['lng']} {cord['lat']}"
                        first_cord = cord
                        print(string)
                    else:
                        string = string + f", {cord['lng']} {cord['lat']}"
                        
                        print(string)
                    count = count + 1
                string = string + f", {first_cord['lng']} {first_cord['lat']}"
                string = string + "))"

                data["wkt"] = string
            
                
            elif var[i][0] in type_0:
                xt["key"] = var[i][0]
                xt["value"]["type"] = 0
                xt["value"]["strValue"] = var[i][1]
                map.append(xt)
                
            elif var[i][0] in type_1:
                xt["key"] = var[i][0]
                xt["value"]["type"] = 1
                xt["value"]["fltValue"] = float(var[i][1])
                map.append(xt)

            elif var[i][0] in type_2:
                xt["key"] = var[i][0]
                xt["value"]["type"] = 2
                xt["value"]["intValue"] = int(var[i][1])
                map.append(xt)
                
            elif var[i][0] in type_3:
                xt["key"] = var[i][0]
                xt["value"]["type"] = 3
                xt["value"]["strValue"] = var[i][1]
                map.append(xt)
                
            
            


        print(map)
        print(data)
        id = f'Field_{length + 1}'

        field ={
                    "value0": {
                        "polymorphic_id": 1073741824,
                        "ptr_wrapper": {
                            "id": 2147483649,
                            "data": {
                                "id": id,
                                "idIsURI": False,
                                "components": [
                                    {
                                        "key": {
                                            "polymorphic_id": 2147483649,
                                            "polymorphic_name": "sempr::TriplePropertyMap",
                                            "ptr_wrapper": {
                                                "id": 2147483650,
                                                "data": {
                                                    "base": {},
                                                    "map": []
                                                }
                                            }
                                        },

                                        "value": ""
                                    },
                                    {
                                        "key": {
                                            "polymorphic_id": 2147483650,
                                            "polymorphic_name": "sempr::GeosGeometry",
                                            "ptr_wrapper": {
                                                "id": 2147483651,
                                                "data": {
                                                    "base": {},
                                                    "wkt": ""
                                                }
                                            }
                                        },
                                        "value": "WGS"
                                    }


                                ]
                            }
                        }
                    }
                }
        field["value0"]["ptr_wrapper"]["data"]["components"][0]["key"]["ptr_wrapper"]["data"]["map"] = map
        field["value0"]["ptr_wrapper"]["data"]["components"][1]["key"]["ptr_wrapper"]["data"] = data

        # Convert the dictionary to a JSON string
        field_json = json.dumps(field, indent=4)

        # Write the JSON string to a file
        with open(f'db/{id}.json', 'w') as f:
            f.write(field_json)