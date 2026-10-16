from datetime import date, datetime

import pytest

from app import status_for_quantity
from inventory import InventoryItem
from inventory_service import InventoryItemService


@pytest.fixture
def service():
    return InventoryItemService()


def make_item(
    title="Shipping cartons",
    description="Reinforced packing material",
    category="Packaging",
    quantity=4,
    status="Low stock",
    supplier="North Supply",
    item_id=0,
):
    return InventoryItem(
        Id=item_id,
        Title=title,
        Description=description,
        Category=category,
        Quantity=quantity,
        Status=status,
        Supplier=supplier,
        LastUpdatedDate=datetime(2026, 10, 16, 9, 0),
        ReorderDate=date(2026, 11, 1),
    )


def test_add_assigns_id_and_returns_item(service):
    item = make_item()

    result = service.Add(item)

    assert result is item
    assert item.Id == 1
    assert service.GetById(1) is item


def test_get_all_returns_all_items(service):
    first_item = service.Add(make_item())
    second_item = service.Add(make_item(title="Desk lamp", status="In stock"))

    assert service.GetAll() == [first_item, second_item]


def test_get_by_id_returns_item_or_none(service):
    item = service.Add(make_item())

    assert service.GetById(item.Id) is item
    assert service.GetById(999) is None


def test_update_replaces_item_with_matching_id(service):
    stored_item = service.Add(make_item())
    updated_item = make_item(title="Updated cartons", item_id=stored_item.Id)

    assert service.Update(updated_item) is True
    assert service.GetById(stored_item.Id) is updated_item
    assert service.GetById(stored_item.Id).Title == "Updated cartons"
    assert service.Update(make_item(item_id=999)) is False


def test_update_changes_status_and_supplier_for_matching_id(service):
    first_item = service.Add(make_item(title="Shipping cartons"))
    target_item = service.Add(
        make_item(title="Desk lamp", status="In stock", supplier="Bright Goods")
    )
    updated_item = make_item(
        title=target_item.Title,
        status="Low stock",
        supplier="Updated Supplier",
        item_id=target_item.Id,
    )

    assert service.Update(updated_item) is True

    assert service.GetById(target_item.Id).Status == "Low stock"
    assert service.GetById(target_item.Id).Supplier == "Updated Supplier"
    assert service.GetById(first_item.Id) is first_item
    assert first_item.Status == "Low stock"
    assert first_item.Supplier == "North Supply"


def test_search_matches_case_insensitively(service):
    cartons = service.Add(make_item())
    lamp = service.Add(make_item(title="Desk lamp", supplier="Bright Goods"))

    assert service.Search("SHIPPING") == [cartons]
    assert service.Search("bright goods") == [lamp]
    assert service.Search("") == [cartons, lamp]


def test_search_by_id_or_name(service):
    cartons = service.Add(make_item())
    lamp = service.Add(make_item(title="Desk lamp"))

    assert service.SearchByIdOrName(str(lamp.Id)) == [lamp]
    assert service.SearchByIdOrName("SHIPPING") == [cartons]
    assert service.SearchByIdOrName("") == [cartons, lamp]
    assert service.SearchByIdOrName("not found") == []


def test_filter_by_status_matches_case_insensitively(service):
    low_stock = service.Add(make_item())
    service.Add(make_item(title="Desk lamp", status="In stock"))

    assert service.FilterByStatus("LOW STOCK") == [low_stock]
    assert service.FilterByStatus("Unavailable") == []


@pytest.mark.parametrize(
    "category",
    ["Packaging", "Office supplies", "Electronics"],
)
def test_category_values_are_preserved(service, category):
    item = service.Add(make_item(category=category))

    assert item.Category == category
    assert service.GetById(item.Id).Category == category


@pytest.mark.parametrize(
    ("quantity", "expected_status"),
    [
        (0, "Out of stock"),
        (1, "Low stock"),
        (5, "Low stock"),
        (6, "In stock"),
    ],
)
def test_quantity_maps_to_expected_status(quantity, expected_status):
    assert status_for_quantity(quantity) == expected_status