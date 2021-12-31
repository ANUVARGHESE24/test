# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    invoice_number = fields.Many2one(
        comodel_name="account.move",
        index=True, ondelete='cascade',
        string="Invoice Number",
        domain="[('partner_id', '=', partner_id),('state', 'not in', ('draft', 'cancel')),('amount_residual', '!=', 0.00)]",
    )

    amount_residual = fields.Monetary(
        related='invoice_number.amount_residual',
        string="Amount Due",
        domain="[('invoice_number', '=', name)]",
        digits=(10, 2), store=True,
    )
