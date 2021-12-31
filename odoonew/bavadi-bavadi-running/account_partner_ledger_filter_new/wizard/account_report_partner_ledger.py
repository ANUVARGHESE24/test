from odoo import fields, models


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"

    partner_ids = fields.Many2many('res.partner', 'partner_ledger_partner_rel', 'id', 'partner_id', string='Partners')

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled,
                             'amount_currency': self.amount_currency,
                             'partner_ids': self.partner_ids.ids,
                             'operating_unit': self.operating_unit.id,
                             'operating_unit_name': self.operating_unit.name})

        return self.env.ref('base_accounting_kit.action_report_partnerledger').report_action(self, data=data)
