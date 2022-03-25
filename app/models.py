from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object id")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Pet(BaseModel):
    pet_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ptype: str = Field(...)
    gender: str = Field(...)
    size: str = Field(...)
    age: str = Field(...)
    photo: Optional[list] = []
    good_with_children: bool = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "ptype": "Dog",
                "gender": "male",
                "size": "small",
                "age": "baby",
                "photo": ["/pets/pet_photo1.jpg", "/pets/pet_photo2.jpg", "/pets/pet_photo3.jpg"],
                "good_with_children": True
            }
        }


class Customer(BaseModel):
    customer_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    phone: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "phone": "+251912345678",
            }
        }


class Adoption(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ptype: str = Field(...)
    gender: str = Field(...)
    size: str = Field(...)
    age: str = Field(...)
    good_with_children: bool = Field(...)
    name: str = Field(...)
    phone: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "phone": "+251912345678",
                "ptype": "Dog",
                "gender": "male",
                "size": "small",
                "age": "baby",
                "good_with_children": True
            }
        }


class PetRequestModel(BaseModel):
    ptype: Optional[str]
    gender: Optional[str]
    size: Optional[str]
    age: Optional[str]
    good_with_children: Optional[bool]
    limit: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "ptype": "Dog",
                "gender": "male",
                "size": "small",
                "age": "baby",
                "good_with_children": True,
                'limit': 0
            }
        }


class ReportRequestModel(BaseModel):
    from_date: str = Field(...)
    to_date: str = Field(...)


class AdoptionRequestModel(BaseModel):
    customer_id: str = Field(...)
    pet_id: str = Field(...)
