from fastapi.testclient import TestClient
from main import app

# Create test client for API testing
test_client = TestClient(app)

def test_api_health_check():
    """Test that the API health endpoint is working"""
    health_response = test_client.get("/")
    assert health_response.status_code == 200
    assert "API" in health_response.json()["message"]

def test_csv_file_upload():
    """Test uploading a CSV file with product data"""
    with open("products.csv", "rb") as csv_file:
        upload_response = test_client.post("/upload", files={"file": ("products.csv", csv_file, "text/csv")})
    
    assert upload_response.status_code == 200
    response_data = upload_response.json()
    assert "stored" in response_data
    assert "failed" in response_data
    assert isinstance(response_data["failed"], list)

def test_get_products_list():
    """Test retrieving the list of products"""
    products_response = test_client.get("/products")
    assert products_response.status_code == 200
    products_data = products_response.json()
    assert isinstance(products_data, list)
    assert len(products_data) > 0
    assert "name" in products_data[0]

def test_search_products_by_brand():
    """Test filtering products by brand name"""
    search_response = test_client.get("/products/search?brand=StreamThreads")
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert isinstance(search_results, list)
    for product_item in search_results:
        assert product_item["brand"] == "StreamThreads"