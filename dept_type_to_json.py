"""
This file converts the department_types.csv to .json format with the key being the department name.
Code from https://www.geeksforgeeks.org/convert-csv-to-json-using-python/
"""

import csv 
import json 

def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    #convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)
          
csvFilePath = r'department_types.csv'
jsonFilePath = r'department_types.json'
csv_to_json(csvFilePath, jsonFilePath)

# import csv
# import json


# # Function to convert a CSV to JSON
# # Takes the file paths as arguments
# def make_json(csvFilePath, jsonFilePath):
	
# 	# create a dictionary
# 	data = {}
	
# 	# Open a csv reader called DictReader
# 	with open(csvFilePath, encoding='utf-8') as csvf:
# 		csvReader = csv.DictReader(csvf)
		
# 		# Convert each row into a dictionary
# 		# and add it to data
# 		for rows in csvReader:
			
# 			data.append(rows)

# 	# Open a json writer, and use the json.dumps()
# 	# function to dump data
# 	with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
# 		jsonf.write(json.dumps(data, indent=4))
		
# # Driver Code

# # Decide the two file paths according to your
# # computer system
# csvFilePath = r'department_types.csv'
# jsonFilePath = r'department_types.json'

# # Call the make_json function
# make_json(csvFilePath, jsonFilePath)
