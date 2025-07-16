@frappe.whitelist()
def update(docname, updated):
    updated = json.loads(updated)

    # Fetch existing records from child table
    existing_items = frappe.get_list(
        "Sales Items",
        filters={"parent": docname, "parenttype": "Sales"},
        fields=["name", "name1", "qty", "rate", "amount", "idx"]
    )

    existing_map = {(item.name1, item.idx): item for item in existing_items}
    updated_keys = set()

    total_amount = 0

    for idx, item in enumerate(updated, start=1):
        name1 = item.get("name1")
        qty = float(item.get("qty"))
        rate = float(item.get("rate"))
        amount = qty * rate
        total_amount += amount
        key = (name1, idx)
        updated_keys.add(key)

        if key in existing_map:
            existing = existing_map[key]
            # Check for changes
            if float(existing.qty) != qty or float(existing.rate) != rate:
                # Update only if there's a change
                frappe.db.set_value("Sales Items", existing.name, {
                    "qty": qty,
                    "rate": rate,
                    "amount": amount
                })
        else:
            # New row: insert it
            frappe.get_doc({
                "doctype": "Sales Items",
                "parent": docname,
                "parenttype": "Sales",
                "parentfield": "choose_items",
                "name1": name1,
                "qty": qty,
                "rate": rate,
                "amount": amount,
                "idx": idx
            }).insert(ignore_permissions=True)

    # Delete removed rows
    for key, item in existing_map.items():
        if key not in updated_keys:
            frappe.delete_doc("Sales Items", item.name)

    # Update total amount
    frappe.db.set_value("Sales", docname, "total_amount", total_amount)

    frappe.db.commit()
    return "Sales updated successfully"
