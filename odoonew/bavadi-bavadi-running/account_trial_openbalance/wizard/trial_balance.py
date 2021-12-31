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

from odoo import fields, models, api, _
from odoo.tools import date_utils, io, xlsxwriter
import json
import base64
from odoo.tools.misc import get_lang
import logging


class AccountBalanceReport(models.TransientModel):

    _inherit = 'account.balance.report'
    _description = 'Trial Balance Report'


    journal_ids = fields.Many2many('account.journal',
                                   'account_balance_report_journal_rel',
                                   'account_id', 'journal_id',
                                   string='Journals', required=True,
                                   default=[])
    # @pk custom field for branch filter
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit')
    department_id = fields.Many2one('hr.department', 'Department')
    end_date = fields.Date(string='Last Date')


    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'operating_unit': self.operating_unit.id,
                             'operating_unit_name': self.operating_unit.name,
                             'department_id': self.department_id.id,
                             'department_id_name': self.department_id.name,
                             'end_date': self.end_date

                             })
        records = self.env[data['model']].browse(data.get('ids', []))
        # self.env.ref('base_accounting_kit.action_report_trial_balance').report_file = "Trial_Balance"
        return self.env.ref(
            'base_accounting_kit.action_report_trial_balance').with_context(
            landscape=True).report_action(
            records, data=data)

    def get_xlsx_report(self):
        self.ensure_one()
        data = {
            'ids': self.env.context.get('active_ids', []),
            'model': self.env.context.get('active_model', 'ir.ui.menu'),
            'form': self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'display_account', 'company_id'])[
                0],
        }
        data['form'].update({'operating_unit': self.operating_unit.id,
                             'operating_unit_name': self.operating_unit.name,
                             'department_id': self.department_id.id,
                             'department_id_name': self.department_id.name
                             })
        records = self.env[data['model']].browse(data.get('ids', []))
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        self.env.ref('base_accounting_kit.action_report_trial_balance_excel').report_file = "Trial_Balance"
        return self.env.ref('base_accounting_kit.action_report_trial_balance_excel').report_action(records, data=data)


class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"

    end_date = fields.Date(string='Last Date')

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['company_id'] = data['form']['company_id'][0] or False
        return result

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self.with_context(discard_logo_check=True)._print_report(data)