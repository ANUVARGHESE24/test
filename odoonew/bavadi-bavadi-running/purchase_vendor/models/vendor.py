from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_vendor_bill_checker = fields.Boolean("Direct Vendor Billing", implied_group="purchase_vendor.group_vendor_bill_checker")
