from pydantic import BaseModel, validator
from typing import Optional

class ProductCreate(BaseModel):
    sku: str
    name: str
    brand: str
    color: Optional[str] = None
    size: Optional[str] = None
    mrp: float
    price: float
    quantity: int

    @validator("mrp", "price")
    def must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("value must be non-negative")
        return v

    @validator("quantity")
    def quantity_non_negative(cls, v):
        if v < 0:
            raise ValueError("quantity must be >= 0")
        return v

class ProductOut(BaseModel):
    sku: str
    name: str
    brand: str
    color: Optional[str] = None
    size: Optional[str] = None
    mrp: float
    price: float
    quantity: int

    class Config:
        orm_mode = True
