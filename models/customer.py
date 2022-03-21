from pydantic import BaseModel
from typing import Optional


class Customer(BaseModel):
    name: str
    phone: str
