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
    fhir_bundle:dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

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

    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get-file")
async def get_file_to_load():
    file_path = "src/assets/covid.json"
    with open(file=file_path, mode="r") as file:
        content = file.read()

    return Response(content=content, media_type="application/json")

@app.post("/converter/convert-to-fhir")
async def convertToFhir(file:UploadFile):
    fi = file.file
    json_data:list[dict[str,Any]]= json.load(fi)

    converter = create_fhir_bundle(json_data=json_data)

    return converter
   
@app.post("/converter/convert-from-fhir")
async def convertToJson(file:UploadFile):
    fi = file.file
    json_data:dict[str,Any]= json.load(fi)

    converter = reverse_fhir_bundle(fhir_bundle=json_data)

    return converter
 
       
@app.post("/converter/convert-from-fhir-local")
async def convertToLocalDataToFhir():
    fi = "./assets/covid.json"
    with open(file=fi, mode="r") as file:
        json_data:list[dict[str,Any]]= json.load(file)

    converter = create_fhir_bundle(json_data=json_data)

    return Response(content=converter)
 
       
def check_file_existence(directory:str, filename:str):
    file_path = os.path.join(directory, filename)
    return os.path.isfile(file_path)



data= check_file_existence(directory="src/assets/", filename="covid.json")

print(f'the data value {data}')