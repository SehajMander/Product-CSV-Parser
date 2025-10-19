from sqlalchemy.orm import Session
from . import models, schema
from typing import List, Optional

def create_product(db: Session, p: schema.ProductCreate):
    existing = db.query(models.Product).filter(models.Product.sku == p.sku).first()
    if existing:
        return None
    product = models.Product(
        sku=p.sku,
        name=p.name,
        brand=p.brand,
        color=p.color,
        size=p.size,
        mrp=p.mrp,
        price=p.price,
        quantity=p.quantity
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

def search_products(db: Session, brand: Optional[str]=None, color: Optional[str]=None,
                    min_price: Optional[float]=None, max_price: Optional[float]=None,
                    skip: int = 0, limit: int = 100):
    q = db.query(models.Product)
    if brand:
        q = q.filter(models.Product.brand == brand)
    if color:
        q = q.filter(models.Product.color == color)
    if min_price is not None:
        q = q.filter(models.Product.price >= min_price)
    if max_price is not None:
        q = q.filter(models.Product.price <= max_price)
    return q.offset(skip).limit(limit).all()
