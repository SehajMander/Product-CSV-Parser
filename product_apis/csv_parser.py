import csv
from io import StringIO
from typing import Tuple, List, Dict
from .schema import ProductCreate
from pydantic import ValidationError

REQUIRED_FIELDS = ["sku", "name", "brand", "mrp", "price"]

def parse_and_validate_csv(file_bytes) -> Tuple[List[ProductCreate], List[Dict]]:
    """
    Returns (valid_products, failures)
    failures: list of dicts: {row_num, row_data, errors}
    """
    text = file_bytes.decode("utf-8-sig")  # handle BOM
    reader = csv.DictReader(StringIO(text))
    valid = []
    failures = []
    for i, row in enumerate(reader, start=2):  # header is row 1
        # Normalize keys: strip spaces
        row = {k.strip(): (v.strip() if v is not None else "") for k,v in row.items()}
        # Check required fields presence
        missing = [f for f in REQUIRED_FIELDS if not row.get(f)]
        if missing:
            failures.append({"row": i, "row_data": row, "errors": f"missing fields: {missing}"})
            continue
        # convert numeric fields
        try:
            # convert mrp, price to float and quantity to int (default 0 if empty)
            mrp = float(row.get("mrp", 0))
            price = float(row.get("price", 0))
            quantity = int(row.get("quantity", 0)) if row.get("quantity", "") != "" else 0
        except Exception as e:
            failures.append({"row": i, "row_data": row, "errors": f"numeric parse error: {e}"})
            continue
        # rules: price <= mrp, quantity >= 0
        if price > mrp:
            failures.append({"row": i, "row_data": row, "errors": "price > mrp"})
            continue
        if quantity < 0:
            failures.append({"row": i, "row_data": row, "errors": "quantity < 0"})
            continue
        # build ProductCreate Pydantic model (to reuse validators)
        try:
            product = ProductCreate(
                sku=row.get("sku"),
                name=row.get("name"),
                brand=row.get("brand"),
                color=row.get("color") or None,
                size=row.get("size") or None,
                mrp=mrp,
                price=price,
                quantity=quantity
            )
            valid.append(product)
        except ValidationError as ve:
            failures.append({"row": i, "row_data": row, "errors": ve.errors()})
    return valid, failures
