from odoo import api, fields, models


class AccountCharges(models.Model):
    _inherit = 'account.move'

    ship_charge = fields.Monetary(string='Shipping Charges', store=True, readonly=True)
    transport_charge = fields.Monetary(string='Transportation Charges', store=True, readonly=True)
    container_no = fields.Char(string='Container No.')
