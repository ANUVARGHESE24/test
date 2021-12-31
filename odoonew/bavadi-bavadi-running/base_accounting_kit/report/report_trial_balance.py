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

from odoo import api, models, _
from odoo.exceptions import UserError
import logging


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_trial_balance'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Trial Balance Report'

    def _get_accounts(self, accounts, display_account, operating_unit, department_id):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        if operating_unit and not department_id:
            logging.info("operating_unit is called.............")
            tables, where_clause, where_params = self.env[
                'account.move.line'].search([('operating_unit_id', '=', str(operating_unit))])._query_get()
        elif department_id and not operating_unit:
            logging.info("operating_unit is not called.............")
            tables, where_clause, where_params = self.env[
                'account.move.line'].search([('department_id', '=', str(department_id))])._query_get()
        elif department_id and operating_unit:
            logging.info("operating_unit and department is called.............")
            tables, where_clause, where_params = self.env[
                'account.move.line'].search([('department_id', '=', str(department_id)),
                                             ('operating_unit_id', '=', str(operating_unit))])._query_get()
        else:
            logging.info("else is not called.............")
            tables, where_clause, where_params = self.env[
                'account.move.line'].search([])._query_get()
        # logging.info("***************************************************************")
        # logging.info("return tables %s " % tables)
        # logging.info("return where_clause %s " % where_clause)
        # logging.info("return where_params %s " % where_params)
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        params = (tuple(accounts.ids),) + tuple(where_params)
        # logging.info(params)
        # compute the balance, debit and credit for the provided accounts
        if operating_unit and not department_id:
            logging.info("operating_unit is called.............")
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " AND account_move_line.operating_unit_id = " +
                    str(operating_unit) + " GROUP BY account_id")
        elif department_id and not operating_unit:
            logging.info("operating_unit is not called.............")
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " AND account_move_line.department_id = " +
                    str(department_id) + " GROUP BY account_id")
        elif department_id and operating_unit:
            logging.info("operating_unit and department is called.............")
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " AND account_move_line.department_id = " +
                    str(department_id) + " AND account_move_line.operating_unit_id = " +
                    str(operating_unit) + " GROUP BY account_id")
        else:
            logging.info("else is not called.............")
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        # logging.info(request)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(res['debit']) or not currency.is_zero(
                res['credit'])):
                account_res.append(res)
        return account_res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        operating_unit = data['form'].get('operating_unit')
        department_id = data['form'].get('department_id')
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        # logging.info("*************** %s" % docs)
        # docs = self.env[self.model].search([('operating_unit_id', '=', operating_unit)])
        display_account = data['form'].get('display_account')

        accounts = docs if self.model == 'account.account' else self.env[
            'account.account'].search([])
        account_res = self.with_context(
            data['form'].get('used_context'))._get_accounts(accounts,
                                                            display_account, operating_unit, department_id)
        # logging.info("**********************************%s" % self.ids)
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("Trial Balance")
        sheet.set_column(0, 5, 20)
        cell_format = workbook.add_format({'font_size': '12px'})
        bold = workbook.add_format({'bold': True,
                                    'font_size': 10,
                                    })
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                    'border': 1, 'bg_color': '#D3D3D3'})
        txt = workbook.add_format({'font_size': 10, 'bg_color': '#D3D3D3', 'border': 1, 'bold': True})

        txt_left = workbook.add_format({'align': 'left',
                                        'font_size': 10,
                                        })
        amount = workbook.add_format({'align': 'right',
                                      'font_size': 10,
                                      })
        sheet.merge_range('A2:F2', 'Trial Balance', head)
        sheet.write('A6', 'Branch:', bold)
        if data['form']['operating_unit_name']:
            sheet.write('B6', data['form']['operating_unit_name'], cell_format)
        sheet.write('C6', 'Department:', bold)
        if data['form']['department_id_name']:
            sheet.write('D6', data['form']['department_id_name'], cell_format)
        sheet.write('A7', 'From:', bold)
        sheet.write('C7', 'To:', bold)
        if data['form']['date_from'] and data['form']['date_to']:
            sheet.write('B7', data['form']['date_from'], cell_format)
            sheet.write('D7', data['form']['date_to'], cell_format)

        sheet.write('E6', 'Display Account:', bold)
        if data['form']['display_account'] == 'all':
            sheet.write('F6', 'All accounts', cell_format)
        elif data['form']['display_account'] == 'movement':
            sheet.write('F6', 'With movements', cell_format)
        elif data['form']['display_account'] == 'not_zero':
            sheet.write('F6', 'With balance not equal to zero', cell_format)

        sheet.write('E7', 'Target Moves:', bold)
        if data['form']['target_move'] == 'all':
            sheet.write('F7', 'All Entries', cell_format)
        elif data['form']['target_move'] == 'posted':
            sheet.write('F7', 'All Posted Entries', cell_format)

        sheet.write('A9', 'Code', txt)
        sheet.write('B9', 'Account', txt)
        sheet.write('C9', 'Debit (SR)', bold)
        sheet.write('D9', 'Credit (SR)', bold)
        sheet.write('E9', 'Balance (SR)', bold)

        display_account = data['form'].get('display_account')

        operating_unit = data['form'].get('operating_unit')
        department_id = data['form'].get('department_id')
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        accounts = docs if self.model == 'account.account' else self.env[
            'account.account'].search([])
        objects = self.with_context(
            data['form'].get('used_context'))._get_accounts(accounts,
                                                            display_account, operating_unit, department_id)

        row_num = 8
        col_num = 0
        total_debit = 0.0
        total_credit = 0.0
        if objects:
            for i in objects:
                sheet.write(row_num + 1, col_num, str(i['code']), txt)
                sheet.write(row_num + 1, col_num + 1, str(i['name']), txt)
                sheet.write(row_num + 1, col_num + 2, str(round(i['debit'], 2)), txt_left)
                sheet.write(row_num + 1, col_num + 3, str(round(i['credit'], 2)), txt_left)
                sheet.write(row_num + 1, col_num + 4, str(round(i['balance'], 2)), txt_left)
                total_debit += i['debit'] if i['debit'] else 0.0
                total_credit += i['credit'] if i['credit'] else 0.0
                row_num = row_num + 1

            # sheet.write(row_num + 1, col_num + 2, "Total", bold)
            sheet.write(row_num + 1, col_num + 2, str(round(total_debit, 2)), bold)
            sheet.write(row_num + 1, col_num + 3, str(round(total_credit, 2)), bold)
            sheet.write(row_num + 1, col_num + 4,
                        str(round(total_debit, 2) - round(total_credit, 2)), bold)
        # logging.info("*************************** objects %s" % objects)
