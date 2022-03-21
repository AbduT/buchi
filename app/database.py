import datetime
import requests
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pymongo import *

from models import Pet, Customer

client_id = f'prAClspbSEhAkHKNhystmotaXoVtAziB9H8ZqnkAFPWfGUL8zy'
secret = f'rrQDPIpEMlMclJpt8DTmaqOwbT9tifIT5KmWQj4X'
PETFINDER_HOST = "https://api.petfinder.com/v2/"

client = MongoClient('localhost', 27017)
db = client.buchi

petCollection = db.pets
customerCollection = db.customers
adoptionCollection = db.adoptions


async def auth():
    response = requests.post(PETFINDER_HOST + "oauth2/token",
                             json=jsonable_encoder({'grant_type': f"client_credentials",
                                                    'client_id': client_id,
                                                    'client_secret': secret}))
    json_res = response.json()
    return json_res['access_token']


async def get_petfinder_pets(req):
    token = await auth()
    if token:
        res = requests.get(PETFINDER_HOST + "animals", params=jsonable_encoder(req), headers={
            "Authorization": "Bearer " + token
        })
        res_json = res.json()
        animals = res_json['animals']
        pets = []
        for a in animals:
            pets.append({
                'ptype': a['type'],
                'gender': a['gender'],
                'size': a['size'],
                'age': a['age'],
                'photo': a['photos'],
                'good_with_children': a['good_with_children'],
                'source': 'petfinder'
            })
    return pets


async def get_local_pets(filters, limit) -> list:
    pets = petCollection.find(filters, limit=limit).to_list()
    for pet in pets:
        pet['source'] = 'local'

    return pets


async def create_pet(pet: Pet) -> str:
    new_pet = await petCollection.insert_one(jsonable_encoder(pet))
    return str(new_pet.inserted_id)


async def get_pet_by_id(pid: str):
    pet = petCollection.find_one({'_id': ObjectId(pid)})
    return pet


async def get_customer_by_id(cid: str):
    customer = await customerCollection.find_one({'_id': ObjectId(cid)})
    return customer


async def create_customer(customer: Customer) -> str:
    new_customer = petCollection.insert_one(jsonable_encoder(customer))
    return str(new_customer.inserted_id)


async def create_adoption(customer, pet) -> str:
    adoption = customer.dict() + pet.dict()
    adoption['adoption_date'] = datetime.datetime.now()
    na = adoptionCollection.insert_one(adoption)
    return str(na.inserted_id)


async def get_adoption_request(from_date, to_date):
    adoptions = adoptionCollection.find({'adoption_date': {
        '$gte': datetime.datetime.fromisoformat(from_date),
        '$lte': datetime.datetime.fromisoformat(to_date)}})

    return adoptions


async def generate_report(from_date, to_date):
    pipeline = [
        {'$match': {'adoption_date': {
            '$gte': datetime.datetime.fromisoformat(from_date),
            '$lte': datetime.datetime.fromisoformat(to_date)}}
        },
        {
            '$count': 'ptype'
        }
    ]
    adopted_pet_type = adoptionCollection.aggregate(pipeline)
    pipeline = [
        {'$match': {'adoption_date': {
            '$gte': datetime.datetime.fromisoformat(from_date),
            '$lte': datetime.datetime.fromisoformat(to_date)}}
        },
        {
            '$count': 'adoption_date'
        }
    ]
    weekly_adoption_request = adoptionCollection.aggregate(pipeline)
    return {'adoption_pet_type': adopted_pet_type, 'weekly_adoption_request': weekly_adoption_request}