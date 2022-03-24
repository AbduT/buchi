import datetime
import requests
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pymongo import *
from configparser import ConfigParser
from models import Pet, Customer

config = ConfigParser()
config.read('config.conf')

client_id = str(config['PETFINDER']['client_id'])
secret = str(config['PETFINDER']['secret'])
PETFINDER_HOST = str(config['PETFINDER']['api_host'])

host = str(config['MONGO_DB']['host'])
port = int(config['MONGO_DB']['port'])
client = MongoClient(host, port)
db = client.buchi

petCollection = db.pets
customerCollection = db.customers
adoptionCollection = db.adoptions


def auth():
    response = requests.post(PETFINDER_HOST + "oauth2/token",
                             json=jsonable_encoder({'grant_type': f"client_credentials",
                                                    'client_id': client_id,
                                                    'client_secret': secret}))
    json_res = response.json()
    return json_res['access_token']


def get_petfinder_pets(req)-> list:
    token = auth()

    if token:
        res = requests.get(PETFINDER_HOST + "animals", params=jsonable_encoder(req), headers={
            "Authorization": "Bearer " + token
        })
        res_json = res.json()
        if res_json['animals']:
            animals = res_json['animals']
        pets = []
        for a in animals:
            pets.append({
                'ptype': a['type'],
                'gender': a['gender'],
                'size': a['size'],
                'age': a['age'],
                'photo': a['photos'],
                'good_with_children': True,#a['good_with_children'],
                'source': 'petfinder'
            })
    return pets


def get_local_pets(filters, limit) -> list:
    pets =  petCollection.find(filters, limit=limit)
    p = []
    for pet in pets:
        pet['source'] = 'local'
        pet['_id'] = str(pet['_id'])
        pet['pet_id'] = str(pet['_id'])
        p.append(pet)
    return p


async def create_pet(pet: Pet) -> str:
    new_pet = petCollection.insert_one(jsonable_encoder(pet))
    print(new_pet)
    return str(new_pet.inserted_id)


async def get_pet_by_id(pid: str):
    pet = petCollection.find_one({'_id': ObjectId(pid)})
    return pet


async def get_customer_by_id(cid: str):
    customer = customerCollection.find_one({'_id': ObjectId(cid)})
    print(customer)
    return customer


async def create_customer(customer: Customer) -> str:
    new_customer = customerCollection.insert_one(jsonable_encoder(customer))
    return str(new_customer.inserted_id)


async def get_customer_by_phone(phone: str):
    cs = customerCollection.find_one({'phone':phone})
    return cs

async def create_adoption(customer, pet) -> str:
    adoption = {'name': customer['name'],
                'phone': customer['phone'],
                'ptype': pet['ptype'],
                'size': pet['size'],
                'gender': pet['gender'],
                'age': pet['age'],
                'adoption_date': datetime.datetime.now()}
    na = adoptionCollection.insert_one(adoption)
    return str(na.inserted_id)


async def get_adoption_request(from_date, to_date):
    adoptions = adoptionCollection.find({'adoption_date': {
        '$gte': datetime.datetime.fromisoformat(from_date),
        '$lte': datetime.datetime.fromisoformat(to_date)}})

    return adoptions


async def generate_report(from_date, to_date) -> dict:
    ret = {}
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
    for apt in adopted_pet_type:
        print(apt)
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
    if adopted_pet_type:
        ret['adoption_pet_type'] = adopted_pet_type
    if weekly_adoption_request:
        ret['weekly_adoption_request'] = weekly_adoption_request
    return ret