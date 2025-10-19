import csv
from io import StringIO
from typing import Tuple, List, Dict
from .schema import ProductCreate
from pydantic import ValidationError

# Fields that must be present in every CSV row
REQUIRED_FIELDS = ["sku", "name", "brand", "mrp", "price"]

def parse_and_validate_csv(csv_file_bytes) -> Tuple[List[ProductCreate], List[Dict]]:
    """
    Parse CSV file and validate product data
    
    Returns:
        Tuple of (valid_products_list, validation_failures)
        failures: list of dicts with row info and error details
    """
    # Decode file contents, handling BOM if present
    csv_text = csv_file_bytes.decode("utf-8-sig")
    csv_reader = csv.DictReader(StringIO(csv_text))
    
    valid_products = []
    validation_failures = []
    
    # Process each row (starting from row 2 since header is row 1)
    for row_number, csv_row in enumerate(csv_reader, start=2):
        # Clean up the row data - strip whitespace from keys and values
        cleaned_row = {key.strip(): (value.strip() if value is not None else "") 
                      for key, value in csv_row.items()}
        
        # Check if all required fields are present
        missing_fields = [field for field in REQUIRED_FIELDS if not cleaned_row.get(field)]
        if missing_fields:
            validation_failures.append({
                "row": row_number, 
                "row_data": cleaned_row, 
                "errors": f"missing required fields: {missing_fields}"
            })
            continue
            
        # Try to convert numeric fields
        try:
            # Convert pricing fields to float
            mrp_value = float(cleaned_row.get("mrp", 0))
            price_value = float(cleaned_row.get("price", 0))
            # Convert quantity to int, defaulting to 0 if empty
            quantity_value = int(cleaned_row.get("quantity", 0)) if cleaned_row.get("quantity", "") != "" else 0
        except Exception as conversion_error:
            validation_failures.append({
                "row": row_number, 
                "row_data": cleaned_row, 
                "errors": f"numeric conversion error: {conversion_error}"
            })
            continue
            
        # Business rule validation
        if price_value > mrp_value:
            validation_failures.append({
                "row": row_number, 
                "row_data": cleaned_row, 
                "errors": "price cannot be higher than MRP"
            })
            continue
            
        if quantity_value < 0:
            validation_failures.append({
                "row": row_number, 
                "row_data": cleaned_row, 
                "errors": "quantity cannot be negative"
            })
            continue
            
        # Create ProductCreate instance using Pydantic validation
        try:
            new_product = ProductCreate(
                sku=cleaned_row.get("sku"),
                name=cleaned_row.get("name"),
                brand=cleaned_row.get("brand"),
                color=cleaned_row.get("color") or None,
                size=cleaned_row.get("size") or None,
                mrp=mrp_value,
                price=price_value,
                quantity=quantity_value
            )
            valid_products.append(new_product)
        except ValidationError as validation_error:
            validation_failures.append({
                "row": row_number, 
                "row_data": cleaned_row, 
                "errors": validation_error.errors()
            })
            
    return valid_products, validation_failures
