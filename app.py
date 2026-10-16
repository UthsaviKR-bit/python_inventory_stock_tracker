import os
from datetime import date, datetime
from typing import TypedDict

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from inventory import InventoryItem
from inventory_service import InventoryItemService

MAX_SEARCH_LENGTH = 120


def status_for_quantity(quantity: int) -> str:
    if quantity == 0:
        return "Out of stock"
    if quantity <= 5:
        return "Low stock"
    return "In stock"


class ItemFormData(TypedDict):
    title: str
    description: str
    category: str
    supplier: str
    quantity: int
    reorder_date: date


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this"),
    )
    if test_config is not None:
        app.config.update(test_config)

    app.extensions["inventory_item_service"] = InventoryItemService()

    def get_inventory_service():
        return app.extensions["inventory_item_service"]

    def read_item_form() -> ItemFormData:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        supplier = request.form.get("supplier", "").strip()

        try:
            quantity = int(request.form.get("quantity", ""))
        except ValueError as error:
            raise ValueError("Enter a valid quantity.") from error

        try:
            reorder_date = date.fromisoformat(request.form.get("reorder_date", ""))
        except ValueError as error:
            raise ValueError("Enter a valid reorder date.") from error

        if (
            not title
            or not category
            or not supplier
            or quantity < 0
        ):
            raise ValueError("Complete the required fields and use a quantity of zero or more.")

        return {
            "title": title,
            "description": description,
            "category": category,
            "supplier": supplier,
            "quantity": quantity,
            "reorder_date": reorder_date,
        }

    def build_item(values: ItemFormData, item_id: int = 0) -> InventoryItem:
        return InventoryItem(
            Id=item_id,
            Title=values["title"],
            Description=values["description"],
            Category=values["category"],
            Quantity=values["quantity"],
            Status=status_for_quantity(values["quantity"]),
            Supplier=values["supplier"],
            LastUpdatedDate=datetime.now().replace(microsecond=0),
            ReorderDate=values["reorder_date"],
        )

    @app.get("/")
    @app.get("/items")
    def index():
        service = get_inventory_service()
        search_query = request.args.get("q", "").strip()
        all_items = service.GetAll()

        if len(search_query) > MAX_SEARCH_LENGTH:
            flash(f"Search must be {MAX_SEARCH_LENGTH} characters or fewer.", "error")
            items = []
        else:
            items = service.SearchByIdOrName(search_query)

        return render_template(
            "index.html",
            items=items,
            total_count=len(all_items),
            search_query=search_query,
        )

    @app.get("/items/new")
    def create_item_page():
        return render_template(
            "create.html",
            form_action=url_for("add_item"),
            cancel_url=url_for("index"),
            submit_label="Create item",
            item=None,
        )

    @app.post("/items")
    def add_item():
        try:
            values = read_item_form()
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("index"))

        item = get_inventory_service().Add(build_item(values))
        flash(f"{item.Title} added to inventory.", "success")
        return redirect(url_for("index"))

    @app.get("/items/<int:item_id>")
    def item_details(item_id):
        item = get_inventory_service().GetById(item_id)
        if item is None:
            abort(404)
        return render_template("details.html", item=item)

    @app.get("/items/<int:item_id>/edit")
    def edit_item_page(item_id):
        item = get_inventory_service().GetById(item_id)
        if item is None:
            abort(404)
        return render_template(
            "edit.html",
            item=item,
            form_action=url_for("edit_item", item_id=item_id),
            cancel_url=url_for("item_details", item_id=item_id),
            submit_label="Save changes",
        )

    @app.post("/items/<int:item_id>/edit")
    def edit_item(item_id):
        try:
            values = read_item_form()
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("edit_item_page", item_id=item_id))

        service = get_inventory_service()
        if service.GetById(item_id) is None:
            abort(404)
        item = build_item(values, item_id=item_id)
        service.Update(item)
        flash(f"{item.Title} updated.", "success")
        return redirect(url_for("item_details", item_id=item_id))

    @app.post("/items/<int:item_id>/delete")
    def delete_item(item_id):
        if get_inventory_service().Delete(item_id):
            flash("Inventory item removed.", "success")
        else:
            flash("That inventory item was not found.", "error")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)