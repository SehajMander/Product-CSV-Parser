from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from product_apis import models, schema, apis, csv_parser
from product_apis.database import SessionLocal, database_engine, Base

# Initialize the database tables
Base.metadata.create_all(bind=database_engine)

app = FastAPI(title="Products CSV Upload API")

@app.get("/")
def health_check():
    """Simple health check endpoint"""
    return {"message": "API is running! Go to /docs to use the endpoints."}


# Database dependency for dependency injection
def get_db():
    """Get database session for dependency injection"""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process CSV file with product data"""
    if not file.filename.endswith((".csv", ".CSV")):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    # Read file contents
    file_contents = await file.read()
    valid_products_list, parsing_failures = csv_parser.parse_and_validate_csv(file_contents)
    
    # Track results
    successfully_stored = 0
    failed_insertions = []

    # Process each valid product
    for product_data in valid_products_list:
        created_product = apis.create_product(db, product_data)
        if created_product:
            successfully_stored += 1
        else:
            # Either duplicate SKU or insertion failed
            failed_insertions.append({"sku": product_data.sku, "error": "duplicate_or_not_inserted"})
    
    # Combine parsing failures with insertion failures
    failed_insertions.extend(parsing_failures)

    return {
        "message": "CSV uploaded successfully",
        "stored": successfully_stored, 
        "failed": failed_insertions
        }

@app.get("/products", response_model=List[schema.ProductOut])
def list_products(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get paginated list of products"""
    offset = (page - 1) * limit
    product_list = apis.get_products(db, skip=offset, limit=limit)
    return product_list

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
    """Search products with filters and pagination"""
    offset = (page - 1) * limit
    search_results = apis.search_products(db,
                                         brand=brand,
                                         color=color,
                                         min_price=minPrice,
                                         max_price=maxPrice,
                                         skip=offset,
                                         limit=limit)
    return search_results
