import frappe
from frappe.query_builder import Order
from frappe.utils import getdate, format_datetime
from datetime import datetime


@frappe.whitelist()
def get_notifications():
    Notification = frappe.qb.DocType("CRM Notification")
    query = (
        frappe.qb.from_(Notification)
        .select("*")
        .where(Notification.to_user == frappe.session.user)
        .orderby("creation", order=Order.desc)
    )
    notifications = query.run(as_dict=True)

    _notifications = []
    for notification in notifications:
        _notifications.append(
            {
                "creation": notification.creation,
                "from_user": {
                    "name": notification.from_user,
                    "full_name": frappe.get_value(
                        "User", notification.from_user, "full_name"
                    ),
                },
                "type": notification.type,
                "to_user": notification.to_user,
                "read": notification.read,
                "comment": notification.comment,
                "notification_text": notification.notification_text,
                "notification_type_doctype": notification.notification_type_doctype,
                "notification_type_doc": notification.notification_type_doc,
                "reference_doctype": (
                    "deal" if notification.reference_doctype == "CRM Deal" else "lead"
                ),
                "reference_name": notification.reference_name,
                "route_name": (
                    "Deal" if notification.reference_doctype == "CRM Deal" else "Lead"
                ),
            }
        )

    return _notifications


@frappe.whitelist()
def mark_as_read(user=None, doc=None):
    user = user or frappe.session.user
    filters = {"to_user": user, "read": False}
    or_filters = []
    if doc:
        or_filters = [
            {"comment": doc},
            {"notification_type_doc": doc},
        ]
    for n in frappe.get_all("CRM Notification", filters=filters, or_filters=or_filters):
        d = frappe.get_doc("CRM Notification", n.name)
        d.read = True
        d.save()

import frappe
from frappe.utils import getdate, format_datetime
from datetime import datetime

import frappe
from frappe.utils import getdate, format_datetime
from datetime import datetime

import frappe
from frappe.utils import getdate, format_datetime
from datetime import datetime

def create_task_notification(doc, method):
    # Convert due_date to datetime if it is not None and not already a datetime object
    if isinstance(doc.due_date, str):
        try:
            due_date = getdate(doc.due_date)  # Converts string to date object
            due_date = datetime.combine(due_date, datetime.min.time())  # Converts date to datetime object
        except Exception as e:
            due_date = None
            frappe.log_error(f"Failed to parse due date for task {doc.name}: {str(e)}", "CRM Task Notification Error")
    else:
        due_date = doc.due_date

    # Format due date for display, or use "No due date" if due_date is None
    due_date_text = due_date.strftime("%Y-%m-%d %H:%M") if due_date else "No due date"
    notification_text = f"Task {doc.title} is due on {due_date_text}"

    # Determine the route based on the reference doctype and reference name
    # Determine the route based on the reference doctype and reference name
    reference_name = doc.reference_docname or doc.name
    route_options = {}

    if doc.reference_doctype == "CRM Lead":
        route = ["Form", "CRM Lead", reference_name]
        route_options = {"tab": "tasks"}
    elif doc.reference_doctype == "CRM Deal":
        route = ["Form", "CRM Deal", reference_name]
        route_options = {"tab": "tasks"}
    else:
        route = ["Form", "CRM Task", reference_name]

    # Debugging print to verify the generated route and route_options
    frappe.log_error(f"Generated Route: {route}, Route Options: {route_options}", "Route Debugging")

    # Create the notification document
    notification = frappe.new_doc("CRM Notification")
    notification.update({
        "notification_text": notification_text,
        "reference_doctype": doc.reference_doctype,
        "reference_name": reference_name,
        "to_user": doc.assigned_to,
        "from_user": frappe.session.user,
        "route": route,
        "route_options": route_options
    })
    notification.insert(ignore_permissions=True)

    # Publish real-time update for notifications
    frappe.publish_realtime(
        "crm_notification",
        message={"type": "new", "notification": notification.name},
        user=doc.assigned_to
    )
