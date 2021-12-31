# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReceiptsMenu(models.TransientModel):
    _inherit = "res.config.settings"

    group_customer_receipts = fields.Boolean("Customers Receipts",
                                             implied_group="receipts_menu_hiding.group_customer_receipts")


class VendorsReceipts(models.TransientModel):
    _inherit = "res.config.settings"

    group_vendor_receipts = fields.Boolean("Vendors Receipts",
                                           implied_group="receipts_menu_hiding.group_vendor_receipts")
