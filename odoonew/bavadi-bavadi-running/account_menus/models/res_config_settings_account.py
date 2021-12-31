# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ImportInvoiceBill(models.TransientModel):
    _inherit = "res.config.settings"

    group_customer_invoice_bill = fields.Boolean("Import Invoice Bill", implied_group="account_menus.group_customer_invoice_bill")


class ImportVendorBill(models.TransientModel):
    _inherit = "res.config.settings"

    group_vendor_bill = fields.Boolean("Import Vendor Bill", implied_group="account_menus.group_vendor_bill")
