#!/usr/bin/env python3
"""
Feature Generator Script
Generates FastAPI feature modules (schemas, service, router) interactively.
"""

import os
import re
from pathlib import Path
from typing import Optional


# Base path for features
BASE_DIR = Path(__file__).parent.parent
FEATURES_DIR = BASE_DIR / "app" / "features"
ROUTER_FILE = BASE_DIR / "app" / "api" / "router.py"


# Type mapping for Pydantic
TYPE_MAP = {
    "str": "str",
    "string": "str",
    "int": "int",
    "integer": "int",
    "float": "float",
    "bool": "bool",
    "boolean": "bool",
    "date": "date",
    "datetime": "datetime",
}


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def to_snake_case(name: str) -> str:
    """Ensure name is snake_case."""
    name = re.sub(r"([A-Z])", r"_\1", name).lower()
    return name.strip("_").replace("-", "_")


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input."""
    suffix = "[Y/n]" if default else "[y/N]"
    result = input(f"{prompt} {suffix}: ").strip().lower()
    if not result:
        return default
    return result in ("y", "yes")


def get_fields() -> list[dict]:
    """Interactively get field definitions."""
    fields = []
    print("\n📝 Define fields (empty name to finish):")
    print("   Types: str, int, float, bool, date, datetime")
    
    while True:
        name = get_input("   Field name").strip()
        if not name:
            break
        
        field_type = get_input("   Field type", "str").lower()
        field_type = TYPE_MAP.get(field_type, "str")
        
        optional = get_yes_no("   Optional?", False)
        
        fields.append({
            "name": to_snake_case(name),
            "type": field_type,
            "optional": optional,
        })
        print()
    
    return fields


def get_endpoints() -> dict:
    """Interactively select which endpoints to generate."""
    print("\n🔌 Select endpoints to generate:")
    return {
        "get_list": get_yes_no("   GET /{name} (list all)", True),
        "get_one": get_yes_no("   GET /{name}/{id} (get one)", True),
        "create": get_yes_no("   POST /{name} (create)", True),
        "update": get_yes_no("   PUT /{name}/{id} (update)", True),
        "delete": get_yes_no("   DELETE /{name}/{id} (delete)", False),
    }


def generate_schemas(feature_name: str, fields: list[dict]) -> str:
    """Generate schemas.py content."""
    pascal = to_pascal_case(feature_name)
    
    # Check if we need date imports
    needs_date = any(f["type"] == "date" for f in fields)
    needs_datetime = any(f["type"] == "datetime" for f in fields)
    
    imports = ["from typing import Optional", "from datetime import datetime"]
    if needs_date:
        imports[1] = "from datetime import date, datetime"
    
    imports.append("from pydantic import BaseModel, Field")
    
    # Build field lines
    base_fields = []
    create_fields = []
    update_fields = []
    
    for f in fields:
        ftype = f["type"]
        if f["optional"]:
            base_fields.append(f'    {f["name"]}: Optional[{ftype}] = None')
            create_fields.append(f'    {f["name"]}: Optional[{ftype}] = None')
        else:
            base_fields.append(f'    {f["name"]}: {ftype}')
            create_fields.append(f'    {f["name"]}: {ftype}')
        update_fields.append(f'    {f["name"]}: Optional[{ftype}] = None')
    
    return f'''"""
{pascal} schemas (Pydantic models).
"""

{chr(10).join(imports)}


class {pascal}Base(BaseModel):
    """Base {feature_name} schema."""
{chr(10).join(base_fields) if base_fields else "    pass"}


class {pascal}Create({pascal}Base):
    """Schema for creating a new {feature_name}."""
    pass


class {pascal}Update(BaseModel):
    """Schema for updating a {feature_name}."""
{chr(10).join(update_fields) if update_fields else "    pass"}


class {pascal}Response({pascal}Base):
    """Schema for {feature_name} response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class {pascal}ListResponse(BaseModel):
    """Schema for paginated {feature_name} list."""
    items: list[{pascal}Response]
    total: int
    page: int
    page_size: int
'''


def generate_service(feature_name: str, fields: list[dict]) -> str:
    """Generate service.py content."""
    pascal = to_pascal_case(feature_name)
    
    # Build mock data fields
    mock_fields = []
    for f in fields:
        if f["type"] == "str":
            mock_fields.append(f'            "{f["name"]}": "Sample {f["name"]}",')
        elif f["type"] == "int":
            mock_fields.append(f'            "{f["name"]}": 1,')
        elif f["type"] == "float":
            mock_fields.append(f'            "{f["name"]}": 1.0,')
        elif f["type"] == "bool":
            mock_fields.append(f'            "{f["name"]}": True,')
        elif f["type"] == "date":
            mock_fields.append(f'            "{f["name"]}": date.today(),')
        elif f["type"] == "datetime":
            mock_fields.append(f'            "{f["name"]}": datetime.now(),')
    
    mock_data = chr(10).join(mock_fields)
    
    return f'''"""
{pascal} service - Business logic.
"""

from typing import List, Optional
from datetime import date, datetime

from app.core.exceptions import NotFoundException
from app.features.{feature_name}.schemas import {pascal}Create, {pascal}Update


class {pascal}Service:
    """Service class for {feature_name} operations."""

    def __init__(self, db=None):
        self.db = db

    def get_all(self, page: int = 1, page_size: int = 10) -> tuple[List[dict], int]:
        """Get paginated list."""
        # TODO: Replace with actual database query
        items = [
            {{
                "id": 1,
{mock_data}
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }},
        ]
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end], total

    def get_by_id(self, item_id: int) -> dict:
        """Get by ID."""
        if item_id > 100:
            raise NotFoundException(f"{pascal} with id {{item_id}} not found")
        return {{
            "id": item_id,
{mock_data}
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }}

    def create(self, data: {pascal}Create) -> dict:
        """Create new item."""
        return {{
            "id": 1,
            **data.model_dump(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }}

    def update(self, item_id: int, data: {pascal}Update) -> dict:
        """Update existing item."""
        item = self.get_by_id(item_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            item[key] = value
        item["updated_at"] = datetime.now()
        return item

    def delete(self, item_id: int) -> None:
        """Delete item."""
        self.get_by_id(item_id)  # Verify exists
        # TODO: Delete from database
        pass
'''


def generate_router(feature_name: str, endpoints: dict) -> str:
    """Generate router.py content."""
    pascal = to_pascal_case(feature_name)
    
    # Build import list based on endpoints
    schema_imports = [f"{pascal}Response", f"{pascal}ListResponse"]
    if endpoints["create"]:
        schema_imports.append(f"{pascal}Create")
    if endpoints["update"]:
        schema_imports.append(f"{pascal}Update")
    
    imports = f"""from app.features.{feature_name}.schemas import (
    {", ".join(schema_imports)},
)
from app.features.{feature_name}.service import {pascal}Service"""
    
    # Build endpoint functions
    funcs = []
    
    if endpoints["get_list"]:
        funcs.append(f'''
@router.get("", response_model={pascal}ListResponse)
async def get_{feature_name}(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """Get paginated list of {feature_name}."""
    service = {pascal}Service()
    items, total = service.get_all(page=page, page_size=page_size)
    return {pascal}ListResponse(items=items, total=total, page=page, page_size=page_size)
''')
    
    if endpoints["get_one"]:
        funcs.append(f'''
@router.get("/{{item_id}}", response_model={pascal}Response)
async def get_{feature_name[:-1] if feature_name.endswith("s") else feature_name}(item_id: int):
    """Get a single {feature_name} by ID."""
    service = {pascal}Service()
    return service.get_by_id(item_id)
''')
    
    if endpoints["create"]:
        funcs.append(f'''
@router.post("", response_model={pascal}Response, status_code=status.HTTP_201_CREATED)
async def create_{feature_name[:-1] if feature_name.endswith("s") else feature_name}(data: {pascal}Create):
    """Create a new {feature_name}."""
    service = {pascal}Service()
    return service.create(data)
''')
    
    if endpoints["update"]:
        funcs.append(f'''
@router.put("/{{item_id}}", response_model={pascal}Response)
async def update_{feature_name[:-1] if feature_name.endswith("s") else feature_name}(item_id: int, data: {pascal}Update):
    """Update an existing {feature_name}."""
    service = {pascal}Service()
    return service.update(item_id, data)
''')
    
    if endpoints["delete"]:
        funcs.append(f'''
@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{feature_name[:-1] if feature_name.endswith("s") else feature_name}(item_id: int):
    """Delete a {feature_name}."""
    service = {pascal}Service()
    service.delete(item_id)
''')
    
    return f'''"""
{pascal} router - API endpoints.
"""

from fastapi import APIRouter, Query, status

{imports}

router = APIRouter()
{"".join(funcs)}
'''


def update_v1_router(feature_name: str) -> None:
    """Add feature router to v1 router."""
    pascal = to_pascal_case(feature_name)
    
    with open(ROUTER_FILE, "r") as f:
        content = f.read()
    
    # Add import
    import_line = f"from app.features.{feature_name}.router import router as {feature_name}_router"
    if import_line not in content:
        # Find last import or api_router line
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_idx = i + 1
        lines.insert(insert_idx, import_line)
        content = "\n".join(lines)
    
    # Add include_router
    include_line = f'api_router.include_router({feature_name}_router, prefix="/{feature_name}", tags=["{pascal}"])'
    if include_line not in content:
        content = content.rstrip() + f"\n{include_line}\n"
    
    with open(ROUTER_FILE, "w") as f:
        f.write(content)


def main():
    print("=" * 50)
    print("🚀 FastAPI Feature Generator")
    print("=" * 50)
    
    # Get feature name
    feature_name = get_input("\n📦 Feature name (e.g., kosts, regions)")
    feature_name = to_snake_case(feature_name)
    
    if not feature_name:
        print("❌ Feature name is required")
        return
    
    # Get fields
    fields = get_fields()
    
    # Get endpoints
    endpoints = get_endpoints()
    
    # Create feature directory
    feature_dir = FEATURES_DIR / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate files
    print(f"\n📁 Generating {feature_name} feature...")
    
    # __init__.py
    (feature_dir / "__init__.py").write_text("")
    print(f"   ✅ {feature_name}/__init__.py")
    
    # schemas.py
    (feature_dir / "schemas.py").write_text(generate_schemas(feature_name, fields))
    print(f"   ✅ {feature_name}/schemas.py")
    
    # service.py
    (feature_dir / "service.py").write_text(generate_service(feature_name, fields))
    print(f"   ✅ {feature_name}/service.py")
    
    # router.py
    (feature_dir / "router.py").write_text(generate_router(feature_name, endpoints))
    print(f"   ✅ {feature_name}/router.py")
    
    # Update v1 router
    update_v1_router(feature_name)
    print(f"   ✅ Updated api/v1/router.py")
    
    print(f"\n🎉 Feature '{feature_name}' generated successfully!")
    print(f"   Restart server to see new endpoints in Swagger: /docs")


if __name__ == "__main__":
    main()
