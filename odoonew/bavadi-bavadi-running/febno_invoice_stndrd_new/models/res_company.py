from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    iban1 = fields.Char(string="IBAN")
    swift1 = fields.Char(string="Swift")
    iban2 = fields.Char(string="IBAN")
    swift2 = fields.Char(string="Swift")



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_custom = fields.Float(compute='_compute_amountcustom', string='Net Price Unit', store=True)


    @api.depends('discount', 'price_unit')
    def _compute_amountcustom(self):
        for line in self:
            price = (line.price_unit * (line.discount or 0.0)) / 100.0
            discount_amount = line.price_unit - price
            line.update({
                'tax_custom': discount_amount
            })
