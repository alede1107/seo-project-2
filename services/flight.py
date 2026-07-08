import requests
import os
from dotenv import load_dotenv
import json

path = os.path.join(os.path.dirname(__file__), "data", "airports.json")
with open(path, "r", encoding="utf-8") as f:
  airports = json.load(f)

airports_by_iata = {
  entry["iata"]: entry for entry in airports.values() if entry["iata"]
  }

load_dotenv()

BASE_URL = "https://api.aviationstack.com/v1"
TOKEN = os.getenv("AVIATIONSTACK_API_KEY")

'''

get_destination_from_flight returns a dictionary

Success:
{
  "success": True,
  "city": <str>,
  "flight_status": "active"
}

Failure:
{
  "success": False,
  "reason" : <str> ("no_active_flight" or "airport_not_in_database")
}

'''

def get_destination_from_flight(flight_number) -> dict:

  flight_number = flight_number.strip().upper()

  response = requests.get(f"{BASE_URL}/flights?access_key={TOKEN}&flight_iata={flight_number}")
  data = response.json()

  active_flight = None

  for elem in data["data"]:
    if elem["flight_status"] == "active":
      active_flight = elem
      break

  if active_flight is None:
    return {"success" : False, "reason" : "no_active_flight"}
  
  else:

    airport = active_flight["arrival"]["iata"]
    airport_info = airports_by_iata.get(airport)

    if airport_info is None:
      return {"success" : False, "reason" : "airport_not_in_database"}
    
    city = airport_info["city"]
    state = airport_info["state"]
    country = airport_info["country"]
    
    return {
            "success" : True, 
            "city" : city, 
            "state" : state,
            "country" : country,
            "flight_status" : "active"
            }