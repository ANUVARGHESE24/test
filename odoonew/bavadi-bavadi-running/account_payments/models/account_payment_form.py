# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    name = fields.Many2one(comodel_name="account.move",
                           index=True, ondelete='cascade',
                           string="Invoice Number",
                           domain="[('partner_id', '=', partner_id)]")

    amount_residual = fields.Monetary(related='name.amount_residual',
                                      string="Amount Due",
                                      domain="[('name', '=', name)]",
                                      digits=(10, 2), store=True)
