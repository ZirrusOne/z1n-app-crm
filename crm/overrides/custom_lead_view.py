# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
# import frappe
from frappe import _
from crm.fcrm.doctype.crm_lead.crm_lead import CRMLead

class CustomCRMLead(CRMLead):
	@staticmethod
	def default_list_data():
		columns = [
		   {"label": "Name", "type": "Data", "key": "lead_name", "width": "12rem"}, 
		   {"label": "Organization", "type": "Link", "key": "organization", "options": "CRM Organization", "width": "10rem"},
		   {"label": "Status", "type": "Select", "key": "status", "width": "8rem"}, 
		   {"label": "Email", "type": "Data", "key": "email", "width": "12rem"}, 
		   {"label": "Mobile No", "type": "Data", "key": "mobile_no", "width": "11rem"}, 
		   {"label": "Assigned To", "type": "Text", "key": "_assign", "width": "10rem"}, 
		   {"label": "Last Modified", "type": "Datetime", "key": "modified", "width": "8rem"}, 
		   {"label": "First Name", "type": "Data", "key": "first_name", "width": "10rem"}, 
		   {"label": "Buying Role", "type": "Link", "key": "buying_role", "width": "10rem"}
		]
		rows = [
		   "name", "lead_name", "organization", "status", "email", "mobile_no", "lead_owner", 
		   "first_name", "sla_status", "response_by", "first_response_time", "first_responded_on", 
		   "modified", "_assign", "image", "owner", "creation","modified_by", "_liked_by", "buying_role"
		]
		return {'columns': columns, 'rows': rows}


