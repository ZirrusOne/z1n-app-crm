# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# Scrum-71 - Recently assigned report (10-16-2024)-Anuradha
import frappe
from frappe import _
from datetime import datetime, date

def execute(filters):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "lead_name", "label": _("Lead Name"), "fieldtype": "Link","options": "Lead", "width": 220},
        {"fieldname": "organization", "label": _("Organization"), "fieldtype": "Data", "width": 200},
<<<<<<< HEAD
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 200},
        {"fieldname": "email_id", "label": _("Email Id"), "fieldtype": "Data", "width": 200},
=======
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Link","options": "CRM Lead Status", "width": 200},
        {"fieldname": "email", "label": _("Email Id"), "fieldtype": "Data", "width": 200},
>>>>>>> temp-branch
        {"fieldname": "assigned_to", "label": _("Assigned To"), "fieldtype": "Link", "options": "User", "width": 200},
        {"fieldname": "time_assigned", "label": _("Time Assigned"), "fieldtype": "Data", "width": 200}
    ]

def get_data(filters):
    #get filter condition
    conditions = get_filter_conditions(filters)
<<<<<<< HEAD

    #fetch lead data order by creation date
    lead_details = frappe.db.sql(f"""select  L.name as lead_name, L.company_name as organization, 
                                    L.status as status, L.email_id as email_id, 
                                    (select assigned_by from `tabToDo` where reference_type="Lead" 
                                    and reference_name = L.name) as assigned_to, L.creation as creation
                                   from `tabLead` as L order by L.creation desc""",as_dict=1)
    
=======
    #fetch lead data order by creation date
    lead_details = frappe.db.sql(f"""SELECT l.name, l.lead_name,l.status,l.organization AS organization,
                                            l.email, l.creation, t.allocated_to AS assigned_to
                                     FROM `tabCRM Lead` l LEFT JOIN `tabToDo` t
                                     ON t.reference_type = 'CRM Lead' AND t.reference_name = l.name
                                     WHERE l.docstatus < 2 {conditions}""", as_dict=1)
>>>>>>> temp-branch
    #fetch time if creation date is today else fetch date
    for lead in lead_details:
        if (lead.get('creation')).date() == date.today():
            lead['time_assigned'] = lead.get('creation').strftime('%I:%M %p')
        else:
<<<<<<< HEAD
            lead['time_assigned'] = lead.get('creation').date() 
=======
            lead['time_assigned'] = lead.get('creation').date()
>>>>>>> temp-branch
    return lead_details

def get_filter_conditions(filters):
    conditions = ""
    if filters.from_date:
<<<<<<< HEAD
        conditions += f" date(L.creation) >= {filters.from_date}"
    if filters.to_date:
        conditions += f" and date(L.creation) <= {filters.to_date}"
=======
        conditions += f"and date(l.creation) >= '{filters.from_date}'"
    if filters.to_date:
        conditions += f" and date(l.creation) <= '{filters.to_date}'"
    if filters.assigned_to:
        conditions += f" and t.allocated_to = '{filters.assigned_to}'"
>>>>>>> temp-branch
    return conditions
