from odoo import models, fields, api, _
from odoo.exceptions import UserError



class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_get_invoice_no(self):
        self.action_post()
        self.button_draft()


