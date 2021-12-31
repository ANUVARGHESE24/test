from odoo import api, fields, models

class Preview(models.Model):
    _inherit = 'account.move'

    def preview_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
