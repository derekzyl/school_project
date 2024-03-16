import json
import os
from typing import Any

from fastapi import FastAPI, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app:FastAPI = FastAPI()

origins = [
    
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from datetime import datetime


def create_fhir_bundle(json_data:list[dict[str, Any]]):# -> dict[str, str | list[Any]]:# -> dict[str, str | list[Any]]:
    """
    The function `create_fhir_bundle` takes a list of dictionaries containing COVID-19 data and creates
    a FHIR Bundle resource with Observations for each data entry.
    
    :param json_data: The `json_data` parameter is a list of dictionaries, where each dictionary
    represents a data entry for COVID-19 cases. Each dictionary should have the following keys:
    :type json_data: list[dict[str, Any]]
    :return: The function `create_fhir_bundle` returns a dictionary representing a FHIR Bundle.
    """
    fhir_bundle:dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

    # The line `for entry_data in json_data:` is iterating over each element in the `json_data` list.
    # It assigns each element to the variable `entry_data` one by one, allowing you to perform
    # operations or access the data within each element.
    for entry_data in json_data:
        # Convert date format to "YYYY-MM-DD"
        effective_date = datetime.strptime(entry_data["dateRep"], "%d/%m/%Y").strftime("%Y-%m-%d")

        # Create an Observation for COVID-19 cases
        cases_observation = {
            "resourceType": "Observation",
            "id": f"observation-{entry_data['dateRep']}",
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/who-covid19-case-daily"]
            },
            "subject": {
                "reference": "Patient/afghanistan"
            },
            "effectiveDateTime": effective_date,
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/who-covid19-case-reported-type",
                                "code": "confirmed"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": entry_data["cases"],
                        "unit": "1",
                        "system": "http://unitsofmeasure.org",
                        "code": "1"
                    }
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/who-case-reported-deaths",
                                "code": "reported"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": entry_data["deaths"],
                        "unit": "1",
                        "system": "http://unitsofmeasure.org",
                        "code": "1"
                    }
                }
            ]
        }

        # Add the Observation to the Bundle
        fhir_bundle["entry"].append({"resource": cases_observation})

    return fhir_bundle

# Assuming your JSON data is stored in a variable called json_data

def reverse_fhir_bundle(fhir_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """
    The `reverse_fhir_bundle` function takes a FHIR bundle as input and returns a list of reversed
    entries containing specific data extracted from the bundle.
    
    :param fhir_bundle: The `fhir_bundle` parameter is a dictionary that represents a FHIR bundle. FHIR
    (Fast Healthcare Interoperability Resources) is a standard for exchanging healthcare information
    electronically. The FHIR bundle contains a collection of resources, where each resource represents a
    piece of healthcare data
    :type fhir_bundle: dict[str, Any]
    :return: The function `reverse_fhir_bundle` returns a list of dictionaries, where each dictionary
    represents a reversed entry extracted from the input FHIR bundle.
    """
    reversed_data:list[dict[str, Any]] = []

    for entry in fhir_bundle.get("entry", []):
        observation = entry.get("resource", {})

        # Extract data from the Observation
        effective_date:str = datetime.strptime(observation.get("effectiveDateTime", ""), "%Y-%m-%d").strftime("%d/%m/%Y")
        cases_component:Any = next(
            (
                comp
                for comp in observation.get("component", [])
                if comp.get("code", {}).get("coding", [{}])[0].get("code") == "confirmed"
            ),
            {},
        )
        deaths_component:Any = next(
            (
                comp
                for comp in observation.get("component", [])
                if comp.get("code", {}).get("coding", [{}])[0].get("code") == "reported"
            ),
            {},
        )

        # Create a reversed entry
        reversed_entry:dict[str, Any] = {
            "dateRep": effective_date,
            "day": datetime.strptime(effective_date, "%d/%m/%Y").strftime("%d"),
            "month": datetime.strptime(effective_date, "%d/%m/%Y").strftime("%m"),
            "year": datetime.strptime(effective_date, "%d/%m/%Y").strftime("%Y"),
            "cases": cases_component.get("valueQuantity", {}).get("value", 0),
            "deaths": deaths_component.get("valueQuantity", {}).get("value", 0),
            "countriesAndTerritories": observation.get("subject", {}).get("reference", "").split("/")[-1],
            "geoId": observation.get("subject", {}).get("reference", "").split("/")[-1],
            "countryterritoryCode": observation.get("subject", {}).get("reference", "").split("/")[-1],
            "popData2019": 0,  # You may need to fill in the actual value
            "continentExp": "",  # You may need to fill in the actual value
            "Cumulative_number_for_14_days_of_COVID-19_cases_per_100000": "",  # You may need to fill in the actual value
        }

        reversed_data.append(reversed_entry)

    return reversed_data
def remove_existing_file(file_path: str):
    """
    The function `remove_existing_file` removes a file if it exists at the specified file path.
    
    :param file_path: The file path is a string that represents the location of the file that you want
    to remove. It should include the file name and extension
    :type file_path: str
    """
    if os.path.exists(file_path):
        os.remove(file_path)
def save_json_data(data: list[dict[str, Any]], destination: str):
    """
    The function `save_json_data` saves a list of dictionaries as JSON data to a specified destination
    file.
    
    :param data: The `data` parameter is a list of dictionaries, where each dictionary represents a JSON
    object. Each dictionary should have string keys and values of any type
    :type data: list[dict[str, Any]]
    :param destination: The `destination` parameter is a string that represents the file path where the
    JSON data will be saved
    :type destination: str
    """
    with open(destination, "w") as dest_file:
        json.dump(data, dest_file)
        
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get-file")
async def get_file_to_load():
    """
    The function `get_file_to_load` checks if a file named "file.json" exists in the "src/assets/"
    directory, and if it does, it returns the content of that file as a JSON response.
    :return: a Response object with the content of the file as a string and the media type set to
    "application/json".
    """
    check = check_file_existence(directory= "src/assets/", filename="file.json")
    file_path = "src/assets/covid.json"
    if check:
    
        file_path = "src/assets/file.json"
    with open(file=file_path, mode="r") as file:
        content = file.read()

    return Response(content=content, media_type="application/json")

@app.post("/converter/convert-to-fhir")
async def convertToFhir(file:UploadFile):
    """
    The function `convertToFhir` takes a file as input, reads its contents as JSON data, and creates a
    FHIR bundle using the `create_fhir_bundle` function.
    
    :param file: The `file` parameter is of type `UploadFile`, which is a file-like object that
    represents an uploaded file. It is used to read the contents of the uploaded file
    :type file: UploadFile
    :return: the `converter` object, which is created by calling the `create_fhir_bundle` function with
    the `json_data` as an argument.
    """
    fi = file.file
    json_data:list[dict[str,Any]]= json.load(fi)

    converter = create_fhir_bundle(json_data=json_data)

    return converter
   
@app.post("/converter/convert-from-fhir")
async def convertToJson(file:UploadFile):
    """
    The function `convertToJson` takes an uploaded file, converts it to JSON format, and saves the
    converted JSON data to a specified path.
    
    :param file: The "file" parameter is of type "UploadFile". It represents the uploaded file that
    needs to be converted to JSON
    :type file: UploadFile
    :return: the `converter` variable, which is a dictionary containing the converted JSON data.
    """
    fi = file.file
    json_data:dict[str,Any]= json.load(fi)

    converter = reverse_fhir_bundle(fhir_bundle=json_data)
    save_path = "src/assets/"  # Replace with the desired path
    converted_json_path = os.path.join(save_path, "file.json")
    remove_existing_file(converted_json_path)
    save_json_data(converter, converted_json_path)


    return converter
 
       
@app.post("/converter/convert-from-fhir-local")
async def convertToLocalDataToFhir():
    """
    The function `convertToLocalDataToFhir` reads a JSON file, creates a FHIR bundle from the data, and
    returns the converted data as a response.
    :return: a Response object.
    """
    fi = "./assets/covid.json"
    with open(file=fi, mode="r") as file:
        json_data:list[dict[str,Any]]= json.load(file)

    converter = create_fhir_bundle(json_data=json_data)

    return Response(content=converter)
 
       
def check_file_existence(directory:str, filename:str):
    """
    The function checks if a file exists in a given directory.
    
    :param directory: A string representing the directory where the file is located
    :type directory: str
    :param filename: The filename parameter is a string that represents the name of the file you want to
    check for existence
    :type filename: str
    :return: a boolean value indicating whether the file exists in the specified directory.
    """
    file_path = os.path.join(directory, filename)
    return os.path.isfile(file_path)



data= check_file_existence(directory="src/assets/", filename="covid.json")

print(f'the data value {data}')