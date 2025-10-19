### Products CSV Upload API (FastAPI)

A simple FastAPI service to upload a products CSV, validate rows, store valid products in a SQLite database, and query products with pagination and filters.

---

## Features
- **CSV upload**: Validate rows (required fields, numeric checks, business rules) and store valid products
- **Duplicate handling**: Skips rows that duplicate an existing `sku`
- **List products**: Paginated listing of all products
- **Search products**: Filter by `brand`, `color`, and price range with pagination
- **Auto DB setup**: Creates SQLite tables on startup
- **OpenAPI docs**: Interactive docs at `/docs` and `/redoc`

---

## Tech Stack
- **Python 3.11**
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **SQLite** for persistence
- **Pydantic** for request/response models and validation
- **Uvicorn** ASGI server
- **Pytest** for tests
- Optional: **Docker** for containerized run

---

## Project Structure
```text
.
├─ main.py                      # FastAPI app, routes, dependencies
├─ product_apis/
│  ├─ apis.py                   # DB operations (create/list/search)
│  ├─ csv_parser.py             # CSV parsing and validation
│  ├─ database.py               # SQLAlchemy engine/session/Base
│  ├─ models.py                 # SQLAlchemy models (Product)
│  └─ schema.py                 # Pydantic schemas
├─ products.csv                 # Sample CSV for testing
├─ test_main.py                 # Basic API tests with TestClient
├─ requirements.txt             # Python dependencies
└─ Dockerfile                   # Containerization
```

---

## Getting Started (Local)

### 1) Create and activate a virtual environment
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or Windows cmd
.\.venv\Scripts\activate.bat
# or Git Bash
source .venv/Scripts/activate
```

### 2) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Run the API
```bash
uvicorn main:app --reload --port 8000
```

Now open the docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

SQLite DB file `products.db` is created automatically in the project root on first run.

---

## Running with Docker
```bash
docker build -t products-api:latest .
docker run -p 8000:8000 --name products-api products-api:latest
```

Open `http://localhost:8000/docs`.

To persist the SQLite DB outside the container, you may mount a volume:
```bash
docker run -p 8000:8000 -v $(pwd)/data:/app/data \
  -e DATABASE_URL="sqlite:///./data/products.db" products-api:latest
```

Note: If you change `DATABASE_URL`, also update it in `product_apis/database.py` or make it configurable via env var in code.

---

## CSV Format
The service expects a header row and the following columns (case-sensitive):

- `sku` (required, unique)
- `name` (required)
- `brand` (required)
- `color` (optional)
- `size` (optional)
- `mrp` (required, float, >= 0)
- `price` (required, float, >= 0 and must be <= mrp)
- `quantity` (optional, integer, default 0, must be >= 0)

Example (`products.csv`):
```csv
sku,name,brand,color,size,mrp,price,quantity
SKU-1001,Classic Tee,StreamThreads,Blue,M,999,799,12
SKU-1002,Slim Jeans,StreamDenim,Black,32,1999,1699,5
SKU-1003,Sports Shoes,StreamKicks,White,9,2499,2199,8
```

Validation behavior on upload:
- Rows missing required fields are reported under `failed`
- Non-numeric or invalid numeric values are reported under `failed`
- `price > mrp` or `quantity < 0` are rejected and reported under `failed`
- Duplicate `sku` rows (existing in DB) are skipped and reported

---

## API Endpoints

Base URL: `http://localhost:8000`

### Health Check
- `GET /`
```bash
curl http://localhost:8000/
```
Response:
```json
{ "message": "API is running! Go to /docs to use the endpoints." }
```

### Upload CSV
- `POST /upload`
- Multipart form-data with a single `file` field containing the CSV
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@products.csv;type=text/csv"
```
Sample response fields:
- `stored`: number of rows inserted
- `failed`: array of failure objects with row info and errors

Note: Response currently contains the key `messaeg` instead of `message` in the code.

### List Products (Paginated)
- `GET /products`
- Query params: `page` (default 1, >=1), `limit` (default 10, 1..100)
```bash
curl "http://localhost:8000/products?page=1&limit=10"
```

### Search Products with Filters
- `GET /products/search`
- Query params (all optional):
  - `brand` (exact match)
  - `color` (exact match)
  - `minPrice` (>= 0)
  - `maxPrice` (>= 0)
  - `page` (>= 1)
  - `limit` (1..100)
```bash
curl "http://localhost:8000/products/search?brand=StreamThreads&minPrice=500&maxPrice=1500&page=1&limit=20"
```

---

## Testing
With the app dependencies installed and the server code accessible, run:
```bash
pytest -q
```

The tests in `test_main.py` cover:
- Health endpoint returns 200
- CSV upload returns `stored` and `failed`
- Listing products returns an array with product objects
- Filtering by brand returns matching results only

Tip: Ensure `products.csv` exists in the project root before running tests.

---

## Configuration
- Default DB URL is in `product_apis/database.py`: `sqlite:///./products.db`
- `connect_args={"check_same_thread": false}` is used for SQLite compatibility with FastAPI
- To change DB location/name, update `DATABASE_URL` accordingly

---

## Common Issues
- If you see encoding issues on CSV, UTF-8 with BOM is handled by the parser
- If `products.db` is locked, stop the server/process using it and retry
- Response key on upload is `messaeg` (typo); clients should not rely on it

---

## License
This project is provided as part of an assessment. Add your preferred license if publishing publicly.

---

## Author
Sehajpreet Kaur




