from odoo import api, fields, models
from num2words import num2words

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def amount_to_words(self, amount):
        text_str = str(amount)
        text_str = text_str.split('.', 2)

        text_amount = num2words(int(text_str[0]), lang='en')
        units = num2words(int(text_str[1]), lang='en')

        text_amount = text_amount.capitalize() + " " + self.company_id.currency_id.currency_unit_label + " and " \
                      + units.capitalize() + " " + self.company_id.currency_id.currency_subunit_label
        return text_amount
