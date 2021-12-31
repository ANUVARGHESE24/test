from odoo import api, fields, models


class AccountFields(models.Model):
    _inherit = 'account.move'

    country_origin = fields.Many2one('res.country', string="Country of Origin")
    vessel_no = fields.Char(string='Vessel No.')
