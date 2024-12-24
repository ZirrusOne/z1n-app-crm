# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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
                "reference_docname": reference_docname
            })

    # Save the campaign to apply changes
    campaign.save(ignore_permissions=True)
    frappe.db.commit()

    return {"campaign_name": campaign.name}

        



@frappe.whitelist()
def create_campaign(args):
    existing_campaign = frappe.db.exists("CRM Campaign", {"campaign_name": args.get('campaign_name')})
    if existing_campaign:
        return "Campaign already exist"
    else:
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