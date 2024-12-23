# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMCampaign(Document):
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
def update_campaign_participants(args):
    if args.get('name') and frappe.db.exists("CRM Campaign", args.get('name')):
        campaign = frappe.get_doc("CRM Campaign", args.get('name'))
        
        # Update participants
        existing_names = [participant.get('email') for participant in campaign.get("campaign_participants")]
        if len(args.get("campaign_participants")) > 0:
            for new_participant in args.get("campaign_participants"):
                if new_participant.get('email') not in existing_names:
                    row = campaign.append('campaign_participants', {})
                    row.full_name = new_participant.get('full_name')
                    row.organization = new_participant.get('organization')
                    row.email = new_participant.get('email')
                    row.participant_source = new_participant.get('participant_source')
                    row.reference_docname = new_participant.get('reference_docname')
                else:
                    for exist_participant in campaign.get("campaign_participants"):
                        if exist_participant.get('email') == new_participant.get('email'):
                            for key in ['full_name', 'organization', 'email', 'participant_source', 'reference_docname']:
                                exist_participant.set(key, new_participant.get(key))

        campaign.save(ignore_permissions=True)
        frappe.db.commit()
        return campaign.name



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