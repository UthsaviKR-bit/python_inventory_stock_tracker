from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class InventoryItem:
	Id: int
	Title: str
	Description: str
	Category: str
	Quantity: int
	Status: str
	Supplier: str
	LastUpdatedDate: datetime
	ReorderDate: date
