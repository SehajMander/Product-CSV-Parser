from sqlalchemy.orm import Session
from . import models, schema
from typing import List, Optional

def create_product(db: Session, product_data: schema.ProductCreate):
    """Create a new product in the database if SKU doesn't already exist"""
    # Check if product with this SKU already exists
    existing_product = db.query(models.Product).filter(models.Product.sku == product_data.sku).first()
    if existing_product:
        return None  # SKU already exists
    
    # Create new product instance
    new_product = models.Product(
        sku=product_data.sku,
        name=product_data.name,
        brand=product_data.brand,
        color=product_data.color,
        size=product_data.size,
        mrp=product_data.mrp,
        price=product_data.price,
        quantity=product_data.quantity
    )
    
    # Add to database and commit
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """Retrieve products with pagination"""
    return db.query(models.Product).offset(skip).limit(limit).all()

def search_products(db: Session, brand: Optional[str]=None, color: Optional[str]=None,
                    min_price: Optional[float]=None, max_price: Optional[float]=None,
                    skip: int = 0, limit: int = 100):
    """Search products with optional filters"""
    # Start with base query
    query = db.query(models.Product)
    
    # Apply filters if provided
    if brand:
        query = query.filter(models.Product.brand == brand)
    if color:
        query = query.filter(models.Product.color == color)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    
    # Apply pagination and return results
    return query.offset(skip).limit(limit).all()
