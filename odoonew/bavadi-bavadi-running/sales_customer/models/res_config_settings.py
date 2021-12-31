# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DirectCustomers(models.TransientModel):
    _inherit = "res.config.settings"

    group_customer_invoicing = fields.Boolean("Direct customer invoicing", implied_group="sales_customer.group_customer_invoicing")
