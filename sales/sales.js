frappe.ui.form.on('Sales', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('Update', () => {
                let table_data = frm.doc.choose_items.map(row => ({
                    existing_row_name: row.name,
                   
                    name1:  row.name1,  
                    qty: row.qty,
                    rate: row.rate,
                    amount: row.amount
                }));

                let dialog = new frappe.ui.Dialog({
                    title: 'Update',
                    fields: [
                        {
                            label: 'Choose Items',
                            fieldname: 'choose_items',
                            fieldtype: 'Table',
                            cannot_add_rows: false,
                            in_place_edit: true,
                            data: table_data,
                            fields: [
                                {
                                    label: 'Item',
                                    fieldname: 'name1',
                                    fieldtype: 'Link',
                                    options: 'Items',
                                    in_list_view: true
                                },
                                {
                                    label: 'Rate',
                                    fieldname: 'rate',
                                    fieldtype: 'Int',
                                    in_list_view: true
                                },
                                {
                                    label: 'Qty',
                                    fieldname: 'qty',
                                    fieldtype: 'Int',
                                    in_list_view: true
                                },{
                                    fieldname : 'existing_row_name',
                                    fieldtype: 'Data'
                                }

                            ]
                        }
                    ],
                    primary_action_label: 'Update',
                    primary_action(values) {
                        


                        if(!values.choose_items) {
                            frappe.msgprint('Please add at least one item to update.');
                            return;
                        }
                        for (let item of values.choose_items) {
                            if (!item.name1 || !item.qty || !item.rate || item.qty <= 0 || item.rate <= 0) {
                                frappe.msgprint('Please fill all fields for each item.');
                                return;
                            }
                        }





                        
                        dialog.hide();
                        frappe.call({   
                            method: 'salesapp.salesapp.doctype.sales.sales.update',
                            args: {
                                docname: frm.doc.name,
                                updated: JSON.stringify(values.choose_items)
                            },
                            callback: function (r) {
                                if (r.message) {
                                    frappe.show_alert({
                                        message: r.message,
                                        indicator: 'green'
                                    });
                                    frm.reload_doc();
                                } else {
                                    frappe.show_alert({
                                        message: 'Error updating sales',
                                        indicator: 'red'
                                    });
                                }
                            }
                        });
                        
                    }
                });

                dialog.show();
            });
        }
    },
    name1: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.name1) {
            frappe.db.get_value('Items', row.name1, 'rate', (r) => {
                if (r && r.rate !== undefined) {
                    row.rate = r.rate;
                    frappe.model.set_value(cdt, cdn, 'rate', r.rate);
                    row.amount = (r.rate || 0) * (row.qty || 0);
                    frm.refresh_field('choose_items');
                    update_total_amount(frm);
                }
            });
        }
    },

    qty: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.amount = (row.rate || 0) * (row.qty || 0);
        frm.refresh_field('choose_items');
        update_total_amount(frm);
    },
    
    rate: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.amount = (row.rate || 0) * (row.qty || 0);
        frm.refresh_field('choose_items');
        update_total_amount(frm);
    },

    
});

function update_total_amount(frm) {
    let total = 0;
    (frm.doc.choose_items || []).forEach(row => {
        total += row.amount || 0;
    });
    frm.set_value('total_amount', total);
}
