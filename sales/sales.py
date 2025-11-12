import frappe
from frappe.model.document import Document
import json 


class Sales(Document):
    def validate(self):
        if not self.choose_items:
            frappe.throw("Sales transaction should not be empty")

        self.total_amount = 0
        for i in self.choose_items:
            

            i.amount = i.qty * i.rate
            self.total_amount += i.amount

    def on_update_after_submit(self):
        self.total_amount = 0
        for i in self.choose_items:
            i.amount = i.qty * i.rate
            self.total_amount += i.amount


@frappe.whitelist()
def update(docname, updated):
    import json
    updated = json.loads(updated)
    existing_row =frappe.get_all("Sales Items", filters={"parent": docname}, fields=["name"])
    

    total_amount = 0

    updated_rows = set()

    for item in updated:
        name1 = item.get("name1")
        qty = float(item.get("qty"))
        rate = float(item.get("rate"))
        amount = qty * rate
        total_amount += amount
        row_name = item.get("name")

       

        if row_name and row_name in existing_row:
        
            
            frappe.db.set_value("Sales Items", row_name, {
                "name1": name1,
                "qty": qty,
                "rate": rate,
                "amount": amount
            })
            updated_rows.add(row_name)
        else:
            
            new_row = frappe.new_doc("Sales Items")
            new_row.parent = docname
            new_row.parenttype = "Sales"
            new_row.parentfield = "choose_items"
            new_row.name1 = name1
            new_row.qty = qty
            new_row.rate = rate
            new_row.amount = amount
            
            new_row.insert()
            updated_rows.add(new_row.name)

    for key in existing_row:
        if key.name not in updated_rows:
            frappe.delete_doc("Sales Items", key.name)

    

    
    # # Delete any orphan items (optional safety cleanup)
    # frappe.db.sql("""
    #     DELETE FROM `tabSales Items`
    #     WHERE parent IS NULL OR parent = ''
    # """)

    # Update total amount in Sales
    frappe.db.set_value("Sales", docname, "total_amount", total_amount)

    frappe.db.commit()

    return "Sales updated successfully"

