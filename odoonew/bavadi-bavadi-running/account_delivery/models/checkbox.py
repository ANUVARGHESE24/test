from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_shipping_charge_account_checker = fields.Boolean("Shipping Charges", implied_group="account_delivery.group_shipping_charge_account_checker")
    group_transportation_charge_account_checker = fields.Boolean("Transportation Charges", implied_group="account_delivery.group_transportation_charge_account_checker")
