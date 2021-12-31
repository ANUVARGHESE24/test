from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_import_vendor_bills_checker = fields.Boolean("Import Vendor bills", implied_group="import_menu_activation.group_import_vendor_bills_checker")
    group_import_invoice_bills_checker = fields.Boolean("Import Invoice bills", implied_group="import_menu_activation.group_import_invoice_bills_checker")
