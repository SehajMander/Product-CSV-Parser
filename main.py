from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from product_apis import models, schema, apis, csv_parser
from product_apis.database import SessionLocal, engine, Base

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Products CSV Upload API")

@app.get("/")
def root():
    return {"message": "API is running! Go to /docs to use the endpoints."}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".csv", ".CSV")):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    contents = await file.read()
    valid_products, failures = csv_parser.parse_and_validate_csv(contents)
    stored = 0
    failed = []

    for p in valid_products:
        created = apis.create_product(db, p)
        if created:
            stored += 1
        else:
            # duplicate SKU or not inserted
            failed.append({"sku": p.sku, "error": "duplicate_or_not_inserted"})
    # include parser failures

    failed.extend(failures)

    return {
        "messaeg": "CSV uploaded successfully",
        "stored": stored, 
        "failed": failed
        }

@app.get("/products", response_model=List[schema.ProductOut])
def list_products(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    prods = apis.get_products(db, skip=skip, limit=limit)
    return prods

@app.get("/products/search", response_model=List[schema.ProductOut])
def search_products(
    brand: Optional[str] = None,
    color: Optional[str] = None,
    minPrice: Optional[float] = Query(None, ge=0),
    maxPrice: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    prods = apis.search_products(db,
                                 brand=brand,
                                 color=color,
                                 min_price=minPrice,
                                 max_price=maxPrice,
                                 skip=skip,
                                 limit=limit)
    return prods
