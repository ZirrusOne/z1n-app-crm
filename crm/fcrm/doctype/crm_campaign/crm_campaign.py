# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import time
import pytz
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime
from datetime import datetime

class CRMCampaign(Document):
    def validate(self):
        for i in self.campaign_participants:
            if i.participant_source == "Contact":
                if  frappe.db.exists("Contact", i.reference_docname):
                    i.full_name = frappe.db.get_value("Contact", i.reference_docname,'first_name')
                    i.email = frappe.db.get_value("Contact", i.reference_docname, 'email_id')
            elif i.participant_source == "CRM Lead":
                if frappe.db.exists("CRM Lead", i.reference_docname):
                    i.full_name = frappe.db.get_value("CRM Lead", i.reference_docname,'first_name')
                    i.organization = frappe.db.get_value("CRM Lead", i.reference_docname,'organization')
                    i.email = frappe.db.get_value("CRM Lead", i.reference_docname,'email')

    
    @staticmethod
    def default_list_data():
        columns = [
            {
                'label': 'Campaign Name',
                'type': 'Data',
                'key': 'campaign_name',
                'width': '12rem',
            },
            {
                'label': 'Campaign Type',
                'type': 'Link',
                'key': 'campaign_type',
                'options':'CRM Campaign Type',
                'width': '12rem',
            },
            {
                'label': 'Status',
                'type': 'Select',
                'key': 'status',
                'width': '10rem',
            },
            {
                'label': 'Scheduled Send Time',
                'type': 'Datetime',
                'key': 'scheduled_send_time',
                'width': '11rem',
            }
        ]
        rows = [
            "name",
            "campaign_name",
            "campaign_type",
            "status",
            "scheduled_send_time"
        ]
        return {'columns': columns, 'rows': rows}




@frappe.whitelist()
def update_campaign_participants():
    campaign_name = frappe.form_dict.get("campaign_name")
    doctype = frappe.form_dict.get("doctype")
    campaign_participants = frappe.form_dict.get("campaign_participants")

    if not frappe.db.exists("CRM Campaign",  {"campaign_name": campaign_name}):
        campaign = frappe.new_doc("CRM Campaign")
        campaign.campaign_name = campaign_name
        campaign.insert(ignore_permissions=True)
        frappe.db.commit()
        
    campaign = frappe.get_doc("CRM Campaign", {"campaign_name": campaign_name})

    for participant in campaign_participants:
        reference_docname = participant.get("reference_docname")
        if not frappe.db.exists("CRM Campaign Participants", {"parent": campaign.name, "participant_source": doctype, "reference_docname": reference_docname}):
            campaign.append("campaign_participants", {
                "participant_source": doctype,
                "reference_docname": reference_docname,
            })

    # Save the campaign to apply changes
    campaign.save(ignore_permissions=True)
    frappe.db.commit()

    return {"campaign_name": campaign.name}

def get_campaign():
    campaigns = frappe.db.sql(f"""SELECT cc.name
                              FROM `tabCRM Campaign` cc""", as_dict=True)
    result = [{"label": c['name'], "type": "Data", "value" : c['name']} for c in campaigns]
    return result

@frappe.whitelist()
def create_or_update_campaign(args):
    existing_campaign = frappe.db.exists("CRM Campaign", {"campaign_name": args.get('campaign_name')})
    if existing_campaign:
        #update campaign if any changes on existing record
        campaign = frappe.get_doc("CRM Campaign", args.get('campaign_name'))
        if args.get('campaign_type') != campaign.get('campaign_type'):
            campaign.update({"campaign_type": args.get('campaign_type')})
        if args.get('status') != campaign.get('status'):
            campaign.update({"status": args.get('status')})
        if args.get('scheduled_send_time') != campaign.get('scheduled_send_time'):
            campaign.update({"scheduled_send_time": args.get('scheduled_send_time')})
        if args.get('email_template') != campaign.get('email_template'):
            campaign.update({"email_template": args.get('email_template')})
        campaign.save(ignore_permissions=True)
        frappe.db.commit()
        return campaign.name
    else:
        #create a new campaign if not exist
        campaign = frappe.new_doc("CRM Campaign")
        campaign.update({
            "campaign_name": args.get('campaign_name'),
            "campaign_type": args.get('campaign_type'),
            "status": args.get('status'),
            "scheduled_send_time": args.get('scheduled_send_time'),
            "email_template": args.get('email_template')
        })
        campaign.insert(ignore_permissions=True)
        frappe.db.commit()
        return campaign.name

@frappe.whitelist()
def send_email_for_campaign():
    now = now_datetime()
    print(f"Current server time: {now}, TZ: {now.tzinfo}")

    try:
        campaigns = frappe.get_all(
            "CRM Campaign",
            filters={"status": ["in", ["In Progress"]]},
            fields=["name", "scheduled_send_time"]
        )

        print(f"Found {len(campaigns)} active campaigns")

        for c in campaigns:
            try:
                campaign = frappe.get_doc("CRM Campaign", c.name)
                if not campaign.scheduled_send_time:
                    print(f"Campaign {campaign.name} has no schedule")
                    continue

                print(f"Campaign {campaign.name} - scheduled time: {campaign.scheduled_send_time}")
                
                # Important fix: If both times are naive (no timezone), 
                # compare them directly without timezone conversion
                scheduled = get_datetime(campaign.scheduled_send_time)
                
                # If both have no timezone, compare them directly
                if now.tzinfo is None and scheduled.tzinfo is None:
                    delta = abs((now - scheduled).total_seconds())
                    print(f"Direct comparison of naive datetimes: |{now} - {scheduled}| = {delta}s")
                else:
                    # If either has timezone info, convert both to UTC
                    now_utc = now.astimezone(pytz.UTC) if now.tzinfo else pytz.UTC.localize(now)
                    scheduled_utc = scheduled.astimezone(pytz.UTC) if scheduled.tzinfo else pytz.UTC.localize(scheduled)
                    delta = abs((now_utc - scheduled_utc).total_seconds())
                    print(f"Timezone-aware comparison: |{now_utc} - {scheduled_utc}| = {delta}s")

                if delta <= 60:  # Threshold of 60 seconds
                    print(f"✅ TRIGGERING campaign: {campaign.name}")
                    campaign.status = "In Progress"
                    campaign.save(ignore_permissions=True)
                    
                    for entry in campaign.get("campaign_participants"):
                        send_mail(campaign, entry)
                    
                    campaign.status = "Closed"
                    campaign.save(ignore_permissions=True)
                    print(f"✅ Campaign {campaign.name} completed")
                else:
                    print(f"❌ Skipping {campaign.name}, delta={delta:.1f}s")

            except Exception as e:
                print(f"Error in campaign {c.name}: {str(e)}")
                import traceback
                print(traceback.format_exc())
                
    except Exception as outer:
        print(f"Fatal scheduler error: {str(outer)}")
        import traceback
        print(traceback.format_exc())

def send_mail(campaign, entry):
    try:
        entry_info = entry.as_dict() if hasattr(entry, "as_dict") else dict(entry)

        email = entry_info.get("email")
        if not email:
            # Just log the docname, not the entire record
            frappe.log_error(f"Missing email for {entry_info.get('name')}", "Email Missing")
            return

        email_template_name = campaign.get("email_template")
        if not email_template_name:
            frappe.log_error(f"No template for {campaign.name}", "Template Missing")
            return

        email_template = frappe.get_doc("Email Template", email_template_name)
        
        # Get the participant document for context
        participant_source = entry_info.get("participant_source")
        reference_docname = entry_info.get("reference_docname")
        
        if not participant_source or not reference_docname:
            frappe.log_error(f"Missing reference for {entry_info.get('name')}", "Reference Missing")
            return
            
        context_doc = frappe.get_doc(participant_source, reference_docname)
        context = {"doc": context_doc}

        # Add error handling for template rendering
        try:
            subject = frappe.render_template(email_template.get("subject"), context)
            content = frappe.render_template(email_template.response_, context)
        except Exception as template_error:
            frappe.log_error(str(template_error), "Template Rendering Error")
            return

        # Log more concisely
        print(f"Sending email to: {email} | Subject: {subject[:30]}...")

        comm = make(
            doctype="CRM Campaign",
            name=campaign.name,
            subject=subject,
            content=content,
            recipients=email,
            communication_medium="Email",
            sent_or_received="Sent",
            send_email=True,
            email_template=email_template.name,
        )

        print(f"Communication created: {comm.name}")
        return comm

    except Exception as e:
        # Use a shorter, more specific error log
        frappe.log_error(str(e), f"Mail Send Error: {campaign.name}")


@frappe.whitelist()
def get_doc_view_campaign_data(campaign_name):
    doc = frappe.get_doc("CRM Campaign", campaign_name)
    converted_data = {
            "campaign_name": doc.get('campaign_name'),
            "campaign_type": doc.get('campaign_type'),
            "status": doc.get('status'),
            "scheduled_send_time": doc.get('scheduled_send_time'),
            "email_template": doc.get('email_template')
        }
    campaign_participants = []
    campaign_participants.append({"CRM Lead":get_campaign_participants("CRM Lead", campaign_name)})
    campaign_participants.append({'Contact':get_campaign_participants("Contact", campaign_name)})
    converted_data.update({"campaign_participants":campaign_participants})
    return converted_data

def get_campaign_participants(ref_doctype, campaign_name):
    fields=('name','organization', 'email', 'participant_source', 'reference_docname', 'full_name')
    filters={'parent':campaign_name , 'participant_source':ref_doctype}
    data = frappe.db.get_all("CRM Campaign Participants",filters=filters ,fields=fields)
    for row in data:
        row['name'] = frappe.db.get_value(row.participant_source, {'name':row.reference_docname}, 'name')
    return data if len(data)>0 else []

@frappe.whitelist()
def update_campaign_scheduled_time(campaign_name, scheduled_send_time):
    if not campaign_name or not scheduled_send_time:
        frappe.throw("Campaign Name and Scheduled Send Time are required")

    campaign = frappe.get_doc('CRM Campaign', campaign_name)
    campaign.scheduled_send_time = scheduled_send_time
    campaign.save(ignore_permissions=True)

    return {"status": "success", "campaign_name": campaign.name, "scheduled_send_time": scheduled_send_time}

@frappe.whitelist()
def update_campaign_status(campaign_name, status):
    """
    Update the status of a campaign
    
    Args:
        campaign_name (str): The name of the campaign to update
        status (str): The new status value
    
    Returns:
        dict: A dictionary indicating success and the updated document
    """
    if not frappe.has_permission("CRM Campaign", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Get valid status options to validate input
    valid_statuses = frappe.get_meta("CRM Campaign").get_field("status").options.split("\n")
    valid_statuses = [s.strip() for s in valid_statuses if s.strip()]
    
    # Validate status
    if status not in valid_statuses:
        frappe.throw(_("Invalid status value"), frappe.ValidationError)
    
    # Update the campaign
    campaign = frappe.get_doc("CRM Campaign", campaign_name)
    campaign.status = status
    campaign.save()
    
    return {
        "success": True,
        "data": campaign.as_dict()
    }

@frappe.whitelist()
def get_crm_campaign_meta():
    meta = frappe.get_meta('CRM Campaign')
    status_field = next((f for f in meta.fields if f.fieldname == 'status'), None)
    if not status_field:
        return []
    options = status_field.options.split("\n")
    return [{"label": opt, "value": opt} for opt in options if opt]