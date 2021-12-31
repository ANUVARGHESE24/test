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

import time

from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
from odoo.tools.misc import get_lang

class AccountAgedTrialBalance(models.TransientModel):
    _name = 'account.aged.trial.balance'
    _inherit = 'account.common.partner.report'
    _description = 'Account Aged Trial balance Report'

    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   required=True)
    period_length = fields.Integer(string='Period Length (days)',
                                   required=True, default=30)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))

    # @pk custom field for branch filter
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit')

    def _print_report(self, data):

        res = {}
        data = self.pre_print_report(data)
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        data['form'].update({'operating_unit': self.operating_unit.id,
                             'operating_unit_name': self.operating_unit.name})
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))

        start = data['form']['date_from']

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (
                        str((5 - (i + 1)) * period_length) + '-' + str(
                    (5 - i) * period_length)) or (
                                 '+' + str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        # logging.info("data %s" %data)
        # logging.info("data %s" % data['form']['operating_unit_name'])
        return self.env.ref(
            'base_accounting_kit.action_report_aged_partner_balance').with_context(
            landscape=True).report_action(self, data=data)

    def get_xlsx_report(self):
        self.ensure_one()
        data = {}
        res = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'company_id', 'result_selection', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        data['form'].update({
            'operating_unit': self.operating_unit.id,
            'operating_unit_name': self.operating_unit.name,
        })
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))

        start = data['form']['date_from']

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (
                        str((5 - (i + 1)) * period_length) + '-' + str(
                    (5 - i) * period_length)) or (
                                 '+' + str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        self.env.ref('base_accounting_kit.action_report_aged_partner_balance_excel').report_file = "Aged_Partner_Balance"
        return self.env.ref('base_accounting_kit.action_report_aged_partner_balance_excel').report_action(self,
                                                                                                          data=data)
