# Stockroom Inventory

A Flask inventory tracker with server-rendered list, create, details, and edit pages. Inventory items are stored in memory and reset when the app restarts.

## Run locally

From this directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000. Set the `SECRET_KEY` environment variable before deployment.

## Tests

```powershell
python -m unittest
```

## Project layout

```text
app.py                 Flask application and routes
inventory.py           InventoryItem model
inventory_service.py   In-memory InventoryItemService operations
templates/             List, create, details, and edit pages
static/style.css       Page styles
test_inventory.py      Route tests
```
