from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "API" in response.json()["message"]

def test_upload_csv():
    with open("products.csv", "rb") as f:
        response = client.post("/upload", files={"file": ("products.csv", f, "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert "stored" in data
    assert "failed" in data
    assert isinstance(data["failed"], list)

def test_get_all_products():
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]

def test_filter_by_brand():
    response = client.get("/products/search?brand=StreamThreads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for product in data:
        assert product["brand"] == "StreamThreads"