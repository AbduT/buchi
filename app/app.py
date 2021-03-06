import pathlib
from typing import Optional, List
from uuid import uuid1

from fastapi import FastAPI, status, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse

import database
import models

app = FastAPI()

@app.get('/')
async def redirect_to_docs():
    return RedirectResponse("docs")

@app.post("/create_pet/", response_description="Add a new Pet")
def create_pet(pet: models.Pet):
    new_pet = database.create_pet(pet)
    return {'status':'success', 'pet_id':new_pet}
    #return JSONResponse(status_code=status.HTTP_201_CREATED, content={'status': 'success', 'pet_id': "new_pet"})


@app.get("/get_pets/", description="List Pets From Local Database and PetFinder API with Limit = limit")
async def get_pets(limit: int, ptype: Optional[str] = None,
             gender: Optional[str] = None,
             size: Optional[str] = None,
             age: Optional[str] = None,
             good_with_children: Optional[bool] = None):
    pets = []
    req_dic = {}
    if ptype:
        req_dic['ptype'] = ptype
        req_dic['type'] = ptype
    if gender:
        req_dic['gender'] = gender
    if size:
        req_dic['size'] = size
    if age:
        req_dic['age'] = age
    if good_with_children:
        req_dic['good_with_children'] = good_with_children

    local_pets = database.get_local_pets(req_dic, limit)
    pets.append(local_pets)
    pets_count = len(local_pets)
    petfinders_pet = []
    if pets_count < limit:
        req_dic['limit'] = limit - pets_count
        petfinders_pet = database.get_petfinder_pets(req_dic)
    pets = local_pets + petfinders_pet
    return JSONResponse(status_code=200,content={'status': 'success', 'pets': pets})


@app.post("/add_customer/")
def add_customer(customer: models.Customer):
    c = database.get_customer_by_phone(customer.phone)

    if c: return {'status': 'success', 'customer_id': str(c['_id'])}
    cid = database.create_customer(customer)

    return {'status': 'success', 'customer_id': cid}


@app.post("/adopt/")
def adopt(adoption_request: models.AdoptionRequestModel):
    customer_id = adoption_request.customer_id
    pet_id = adoption_request.pet_id
    customer = database.get_customer_by_id(customer_id)
    pet = database.get_pet_by_id(pet_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    if pet is None:
        raise HTTPException(status_code=404, detail=f"Pet {pet_id} not found")
    adoption = database.create_adoption(customer, pet)
    return {'status': 'success', 'adoption_id': adoption}


@app.get('/get_adoption_request/')
async def get_adoption_request(from_date, to_date):
    adoptions = database.get_adoption_request(from_date,to_date)
    ads = []
    for a in adoptions:
        a['_id']=str(a['_id'])
        a['adoption_date'] = str(a['adoption_date'])
        ads.append(a)
    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': 'success', 'pets': ads})


@app.get('/generate_report')
def generate_report(from_date, to_date):
    data = database.generate_report(from_date,to_date)
    print(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': 'success', 'data': data})


@app.post("/upload_imgs/")
def upload_imgs(imgs: List[UploadFile] = File(...)):
    animal = {}
    if imgs:  # not None:
        photos = []
        for file in imgs:
            sfx = pathlib.Path(file.filename).suffix
            imgName = str(uuid1())+sfx
            try:
                with open('./pets_img/'+imgName, "wb+") as file_object:
                    file_object.write(file.file.read())
            finally:
                file_object.close()
                photos.append(imgName)
        animal['imgs'] = photos
        return {'image_urls': photos}
    else:
        return {'message': 'No Image to Upload'}


@app.get('/pet_images/{img_id}')
def pet_images(img_id: str):
    return FileResponse(path="./pets_img/"+img_id, media_type="image/png")


