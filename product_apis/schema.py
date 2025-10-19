from pydantic import BaseModel, validator
from typing import Optional

class ProductCreate(BaseModel):
    """Schema for creating new products"""
    sku: str
    name: str
    brand: str
    color: Optional[str] = None
    size: Optional[str] = None
    mrp: float
    price: float
    quantity: int

    @validator("mrp", "price")
    def validate_pricing_values(cls, value):
        """Ensure pricing values are not negative"""
        if value < 0:
            raise ValueError("Pricing values must be non-negative")
        return value

    @validator("quantity")
    def validate_quantity(cls, value):
        """Ensure quantity is not negative"""
        if value < 0:
            raise ValueError("Quantity must be greater than or equal to 0")
        return value

class ProductOut(BaseModel):
    """Schema for returning product data"""
    sku: str
    name: str
    brand: str
    color: Optional[str] = None
    size: Optional[str] = None
    mrp: float
    price: float
    quantity: int

    class Config:
        """Pydantic configuration"""
        orm_mode = True  # Enable ORM mode for SQLAlchemy integration
