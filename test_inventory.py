import unittest
from datetime import date, datetime

from app import create_app
from inventory import InventoryItem
from inventory_service import InventoryItemService


class InventoryRouteTests(unittest.TestCase):
	def setUp(self):
		self.app = create_app({"TESTING": True, "SECRET_KEY": "test"})
		self.client = self.app.test_client()

	def make_item(self, title="Shipping cartons", status="Low stock", item_id=0):
		return InventoryItem(
			Id=item_id,
			Title=title,
			Description="Reinforced packing material",
			Category="Packaging",
			Quantity=4,
			Status=status,
			Supplier="North Supply",
			LastUpdatedDate=datetime(2026, 10, 16, 9, 0),
			ReorderDate=date(2026, 11, 1),
		)

	def test_service_add_get_all_and_get_by_id(self):
		service = InventoryItemService()
		item = service.Add(self.make_item())

		self.assertEqual(item.Id, 1)
		self.assertEqual(service.GetAll(), [item])
		self.assertIs(service.GetById(item.Id), item)
		self.assertIsNone(service.GetById(999))

	def test_service_update_and_delete(self):
		service = InventoryItemService()
		item = service.Add(self.make_item())
		item.Title = "Updated cartons"

		self.assertTrue(service.Update(item))
		self.assertEqual(service.GetById(item.Id).Title, "Updated cartons")
		self.assertFalse(service.Update(self.make_item(item_id=999)))
		self.assertTrue(service.Delete(item.Id))
		self.assertEqual(service.GetAll(), [])
		self.assertFalse(service.Delete(item.Id))

	def test_service_search_and_filter_by_status(self):
		service = InventoryItemService()
		low_stock = service.Add(self.make_item())
		in_stock = service.Add(self.make_item(title="Desk lamp", status="In stock"))

		self.assertEqual(service.Search("SHIPPING"), [low_stock])
		self.assertEqual(service.Search("north supply"), [low_stock, in_stock])
		self.assertEqual(service.Search("reinforced"), [low_stock, in_stock])
		self.assertEqual(service.Search("PACKAGING"), [low_stock, in_stock])
		self.assertEqual(service.FilterByStatus("low stock"), [low_stock])
		self.assertEqual(service.Search(""), service.GetAll())

	def test_index_shows_empty_state(self):
		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertIn(b"No inventory yet", response.data)

	def test_create_page_renders(self):
		response = self.client.get("/items/new")

		self.assertEqual(response.status_code, 200)
		self.assertIn(b"Create item", response.data)
		self.assertIn(b'name="reorder_date" type="date" required', response.data)

	def test_add_item_displays_saved_inventory(self):
		response = self.client.post(
			"/items",
			data={
				"title": "Shipping cartons",
				"description": "Medium size",
				"category": "Packaging",
				"quantity": "4",
				"supplier": "North Supply",
				"reorder_date": "2026-11-01",
			},
			follow_redirects=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn(b"Shipping cartons", response.data)
		self.assertIn(b"Low stock", response.data)
		self.assertIn(b"North Supply", response.data)

	def test_inventory_search_matches_id_and_name(self):
		for title in ("Shipping cartons", "Desk lamp"):
			self.client.post(
				"/items",
				data={
					"title": title,
					"category": "General",
					"quantity": "8",
					"supplier": "North Supply",
					"reorder_date": "2026-11-01",
				},
			)

		by_id = self.client.get("/items?q=2")
		by_name = self.client.get("/items?q=SHIPPING")

		self.assertIn(b'href="/items/2">Desk lamp</a>', by_id.data)
		self.assertNotIn(b'href="/items/1">Shipping cartons</a>', by_id.data)
		self.assertIn(b'href="/items/1">Shipping cartons</a>', by_name.data)
		self.assertNotIn(b'href="/items/2">Desk lamp</a>', by_name.data)

	def test_inventory_search_validates_query_length_and_handles_whitespace(self):
		valid_item = {
			"title": "Shipping cartons",
			"category": "General",
			"quantity": "8",
			"supplier": "North Supply",
			"reorder_date": "2026-11-01",
		}
		self.client.post("/items", data=valid_item)

		too_long = self.client.get("/items", query_string={"q": "x" * 121}, follow_redirects=True)
		whitespace = self.client.get("/items", query_string={"q": "   "})

		self.assertIn(b"Search must be 120 characters or fewer", too_long.data)
		self.assertIn(b"No matching inventory", too_long.data)
		self.assertIn(b"Shipping cartons", whitespace.data)

	def test_details_and_edit_pages_render(self):
		self.client.post(
			"/items",
			data={
				"title": "Shipping cartons",
				"category": "Packaging",
				"quantity": "8",
				"supplier": "North Supply",
				"reorder_date": "2026-11-01",
			},
		)

		details = self.client.get("/items/1")
		edit = self.client.get("/items/1/edit")

		self.assertEqual(details.status_code, 200)
		self.assertIn(b"Shipping cartons", details.data)
		self.assertEqual(edit.status_code, 200)
		self.assertIn(b"Save changes", edit.data)

	def test_edit_item_updates_inventory(self):
		self.client.post(
			"/items",
			data={
				"title": "Shipping cartons",
				"category": "Packaging",
				"quantity": "8",
				"supplier": "North Supply",
				"reorder_date": "2026-11-01",
			},
		)

		response = self.client.post(
			"/items/1/edit",
			data={
				"title": "Heavy-duty cartons",
				"category": "Packaging",
				"quantity": "0",
				"supplier": "North Supply",
				"reorder_date": "2026-12-01",
			},
			follow_redirects=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn(b"Heavy-duty cartons", response.data)
		self.assertIn(b"Out of stock", response.data)

	def test_delete_item_removes_saved_inventory(self):
		self.client.post(
			"/items",
			data={
				"title": "Packing tape",
				"category": "Packaging",
				"quantity": "12",
				"supplier": "North Supply",
				"reorder_date": "2026-11-01",
			},
		)

		response = self.client.post("/items/1/delete", follow_redirects=True)

		self.assertEqual(response.status_code, 200)
		self.assertIn(b"No inventory yet", response.data)


if __name__ == "__main__":
	unittest.main()
