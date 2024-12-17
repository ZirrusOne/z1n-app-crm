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
def create_campaign(args):
    campaign = frappe.new_doc("CRM Campaign")
    campaign.update({
        "campaign_name": args.get('campaign_name'),
        "campaign_type": args.get('campaign_type'),
        "status": args.get('status'),
        "scheduled_send_time": args.get('scheduled_send_time'),
        "email_template": args.get('email_template')
    })
    for participant in args.get("campaign_participants"):
        row = campaign.append('campaign_participants', {})
        row.full_name = participant.get('full_name')
        row.organization = participant.get('organization')
        row.email = participant.get('email')
        row.participant_source = participant.get('participant_source')
        row.reference_docname = participant.get('reference_docname')

    campaign.insert(ignore_permissions=True)
    return campaign.name