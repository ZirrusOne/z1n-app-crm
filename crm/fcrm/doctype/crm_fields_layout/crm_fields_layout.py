# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document


class CRMFieldsLayout(Document):
	pass

@frappe.whitelist()
def get_fields_layout(doctype: str, type: str):
	sections = []
	if frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": type}):
		layout = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": type})
	else:
		return []

	if layout.layout:
		sections = json.loads(layout.layout)

	allowed_fields = []
	for section in sections:
		if not section.get("fields"):
			continue
		allowed_fields.extend(section.get("fields"))

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldname in allowed_fields]

	for section in sections:
		for field in section.get("fields") if section.get("fields") else []:
			field = next((f for f in fields if f.fieldname == field), None)
			if field:
				if field.fieldtype == "Select" and field.options:
					field.options = field.options.split("\n")
					field.options = [{"label": _(option), "value": option} for option in field.options]
					field.options.insert(0, {"label": "", "value": ""})
				field = {
					"label": _(field.label),
					"name": field.fieldname,
					"type": field.fieldtype,
					"options": field.options,
					"mandatory": field.reqd,
					"placeholder": field.get("placeholder"),
					"filters": field.get("link_filters")
				}
				section["fields"][section.get("fields").index(field["name"])] = field

	return sections or []


@frappe.whitelist()
def save_fields_layout(doctype: str, type: str, layout: str):
	if frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": type}):
		doc = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": type})
	else:
		doc = frappe.new_doc("CRM Fields Layout")

	doc.update({
		"dt": doctype,
		"type": type,
		"layout": layout,
	})
	doc.save(ignore_permissions=True)

	return doc.layout

@frappe.whitelist()
def get_sidepanel_sections(doctype):
	if not frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": "Side Panel"}):
		return []
	layout = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": "Side Panel"}).layout

	if not layout:
		return []

	layout = json.loads(layout)

	not_allowed_fieldtypes = [
		"Tab Break",
		"Section Break",
		"Column Break",
	]

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in not_allowed_fieldtypes]

	for section in layout:
		section["name"] = section.get("name") or section.get("label")
		for column in section.get("columns") if section.get("columns") else []:
			for field in column.get("fields") if column.get("fields") else []:
				field_obj = next((f for f in fields if f.fieldname == field), None)
				if field_obj:
					field_obj = field_obj.as_dict()
					handle_perm_level_restrictions(field_obj, doctype)
					column["fields"][column.get("fields").index(field)] = get_field_obj(field_obj)

	fields_meta = {}
	for field in fields:
		fields_meta[field.fieldname] = field

	return layout

def handle_perm_level_restrictions(field, doctype, parent_doctype=None):
	if field.permlevel == 0:
		return
	field_has_write_access = field.permlevel in get_permlevel_access("write", doctype, parent_doctype)
	field_has_read_access = field.permlevel in get_permlevel_access("read", doctype, parent_doctype)

	if not field_has_write_access and field_has_read_access:
		field.read_only = 1
	if not field_has_read_access and not field_has_write_access:
		field.hidden = 1


def get_permlevel_access(permission_type="write", doctype=None, parent_doctype=None):
	allowed_permlevels = []
	roles = frappe.get_roles()

	meta = frappe.get_meta(doctype)

	if meta.istable and parent_doctype:
		meta = frappe.get_meta(parent_doctype)
	elif meta.istable and not parent_doctype:
		return [1, 0]

	for perm in meta.permissions:
		if perm.role in roles and perm.get(permission_type) and perm.permlevel not in allowed_permlevels:
			allowed_permlevels.append(perm.permlevel)

	return allowed_permlevels


def get_field_obj(field):
	field["placeholder"] = field.get("placeholder") or "Add " + field.label + "..."

	if field.fieldtype == "Link":
		field["placeholder"] = field.get("placeholder") or "Select " + field.label + "..."
	elif field.fieldtype == "Select" and field.options:
		field["placeholder"] = field.get("placeholder") or "Select " + field.label + "..."
		field["options"] = [{"label": option, "value": option} for option in field.options.split("\n")]

	if field.read_only:
		field["tooltip"] = "This field is read only and cannot be edited."

	return field
