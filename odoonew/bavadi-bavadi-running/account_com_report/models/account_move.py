from odoo import api, fields, models
from num2words import num2words

class AccountInvoice(models.Model):
    _inherit = "account.move"

    text_amount = fields.Char(string="Total Amount In Words", required=False, compute="amount_to_words")

    @api.depends('amount_total')
    def amount_to_words(self):
        text_str = str(self.amount_total)
        text_str = text_str.split('.', 2)

        text_amount = num2words(int(text_str[0]), lang='en')
        units = num2words(int(text_str[1]), lang='en')

        text_amount = text_amount.capitalize() + " " + self.company_id.currency_id.currency_unit_label + " and " \
                      + units.capitalize() + " " + self.company_id.currency_id.currency_subunit_label
        self.text_amount = text_amount