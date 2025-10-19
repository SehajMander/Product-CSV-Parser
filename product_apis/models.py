from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Product(Base):
    """Product model representing items in our inventory"""
    __tablename__ = "products"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product identification
    sku = Column(String, unique=True, index=True, nullable=False)  # Stock Keeping Unit
    
    # Basic product info
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    
    # Optional attributes
    color = Column(String, nullable=True)
    size = Column(String, nullable=True)
    
    # Pricing information
    mrp = Column(Float, nullable=False)  # Maximum Retail Price
    price = Column(Float, nullable=False)  # Current selling price
    
    # Inventory
    quantity = Column(Integer, nullable=False, default=0)
