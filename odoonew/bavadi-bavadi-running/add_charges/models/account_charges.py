from odoo import api, fields, models


class AccountCharges(models.Model):
    _inherit = 'account.move'

    ship_charge = fields.Monetary(string='Shipping Charges', store=True)
    transport_charge = fields.Monetary(string='Transportation Charges', store=True)


