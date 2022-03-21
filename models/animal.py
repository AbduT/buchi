from pydantic import BaseModel
from typing import Optional, List
from fastapi import UploadFile, File


class Animal(BaseModel):
    atype: str
    gender: str
    size: str
    age: str
    photo: Optional[List[str]] = []
    good_with_children: bool


class FupJson(BaseModel):
    img: Optional[UploadFile] = File(...)
    file_name: str
    file_type: str
