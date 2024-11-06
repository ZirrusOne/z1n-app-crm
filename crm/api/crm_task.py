import frappe
from frappe.utils import now_datetime, get_datetime
import pytz
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import get_url_to_form, strip_html
from frappe.desk.doctype.notification_log.notification_log import (
	enqueue_create_notification,
	get_title,
	get_title_html,
)

def update_task_notifications():
	#fetch all task whose due date is today
	task_data= frappe.db.sql(f"""
		select name, status, due_date, title, creation,assigned_to, owner 
		from `tabCRM Task` where status != 'Done' and status != 'Canceled'
		and due_date != 'NULL'
		and DATE_ADD(due_date, INTERVAL 60 SECOND) <= NOW();""",as_dict=1)
	
	if task_data and len(task_data) > 0:
		for task in task_data:
			if frappe.db.exists("CRM Task", task['name']):
				notification_doc = {
					"document_type": "CRM Task",
					"subject": f"Task Due for {task['title']}",
					"document_name": task['name'],
					"from_user": frappe.session.user,
					"email_content": _(f"Task '{task['title']}' has exceeded Due Date. Please take necessary action.")
				}
				if not frappe.db.exists("Notification Log", notification_doc):
					enqueue_create_notification(task['assigned_to'], notification_doc)
