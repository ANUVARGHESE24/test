# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import fields, models


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"

    partner_ids = fields.Many2many('res.partner', 'partner_ledger_partner_rel', 'id', 'partner_id', string='Partners')
    # amount_currency = fields.Boolean("With Currency",
    #                                  help="It adds the currency column on report if the "
    #                                       "currency differs from the company currency.")
    # reconciled = fields.Boolean('Reconciled Entries')
    #
    # # @pk custom field for branch filter
    # operating_unit = fields.Many2one('operating.unit', string='Operating Unit')

    def _print_report(self, data):
        data = self.pre_print_report(data)
        print("data", data)
        # data['form'].update({'reconciled': self.reconciled,
        #                      'amount_currency': self.amount_currency,
        #                      'operating_unit': self.operating_unit.id,
        #                      'operating_unit_name': self.operating_unit.name})
        data['form'].update({'reconciled': self.reconciled,
                             'amount_currency': self.amount_currency,
                             'partner_ids': self.partner_ids.ids,
                             'operating_unit': self.operating_unit.id,
                             'operating_unit_name': self.operating_unit.name
                             })
        return self.env.ref('base_accounting_kit.action_report_partnerledger').report_action(self, data=data)
