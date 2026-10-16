from inventory import InventoryItem


class InventoryItemService:
    def __init__(self):
        """<summary>Create an empty in-memory inventory service.</summary>
        <returns>None</returns>"""
        self._items: list[InventoryItem] = []
        self._next_id = 1

    def Add(self, item: InventoryItem) -> InventoryItem:
        """<summary>Assign an ID to an item and add it to the inventory.</summary>
        <param name="item">The inventory item to add.</param>
        <returns>The added item with its assigned ID.</returns>"""
        item.Id = self._next_id
        self._next_id += 1
        self._items.append(item)
        return item

    def GetAll(self) -> list[InventoryItem]:
        """<summary>Get all items currently in the inventory.</summary>
        <returns>A new list containing the stored inventory items.</returns>"""
        return list(self._items)

    def GetById(self, item_id: int) -> InventoryItem | None:
        """<summary>Find an inventory item by its ID.</summary>
        <param name="item_id">The ID to search for.</param>
        <returns>The matching item, or None if it does not exist.</returns>"""
        return next((item for item in self._items if item.Id == item_id), None)

    def Update(self, item: InventoryItem) -> bool:
        """<summary>Replace the stored item with the same ID.</summary>
        <param name="item">The updated inventory item.</param>
        <returns>True if an item was updated; otherwise, False.</returns>"""
        for index, existing_item in enumerate(self._items):
            if existing_item.Id == item.Id:
                self._items[index] = item
                return True
        return False

    def Delete(self, item_id: int) -> bool:
        """<summary>Remove an inventory item by its ID.</summary>
        <param name="item_id">The ID of the item to remove.</param>
        <returns>True if an item was removed; otherwise, False.</returns>"""
        for index, item in enumerate(self._items):
            if item.Id == item_id:
                del self._items[index]
                return True
        return False

    def Search(self, query: str) -> list[InventoryItem]:
        """<summary>Search item fields using a case-insensitive query.</summary>
        <param name="query">Text to match against item title, description, category, supplier, or status.</param>
        <returns>Matching items, or all items when the query is empty.</returns>"""
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return self.GetAll()
        return [
            item
            for item in self._items
            if normalized_query
            in " ".join(
                (item.Title, item.Description, item.Category, item.Supplier, item.Status)
            ).casefold()
        ]

    def SearchByIdOrName(self, query: str) -> list[InventoryItem]:
        """<summary>Find items by exact ID or partial title, ignoring title case.</summary>
        <param name="query">An item ID or part of an item title.</param>
        <returns>Matching items, or all items when the query is empty.</returns>"""
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return self.GetAll()

        if normalized_query.isdecimal():
            item = self.GetById(int(normalized_query))
            if item is not None:
                return [item]

        return [
            item for item in self._items if normalized_query in item.Title.casefold()
        ]

    def FilterByStatus(self, status: str) -> list[InventoryItem]:
        """<summary>Get inventory items matching a status, ignoring case.</summary>
        <param name="status">The status to match.</param>
        <returns>Items whose status equals the requested status.</returns>"""
        normalized_status = status.strip().casefold()
        return [
            item for item in self._items if item.Status.strip().casefold() == normalized_status
        ]