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
import logging
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportGeneralLedger(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_general_ledger'
    _inherit = "report.report_xlsx.abstract"
    _description = 'General Ledger Report'

    def _get_account_move_entry(self, accounts, init_balance, sortby,
                                display_account, operating_unit):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}
        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.env.context.get('date_from'), date_to=False,
                initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id',
                                           'm').replace('account_move_line',
                                                        'l')
            if operating_unit:
                sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                   '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                   NULL AS currency_id,\
                   '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                   '' AS partner_name\
                   FROM account_move_line l\
                   LEFT JOIN account_move m ON (l.move_id=m.id)\
                   LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                   LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                   LEFT JOIN account_move i ON (m.id =i.id)\
                   JOIN account_journal j ON (l.journal_id=j.id)\
                   WHERE l.account_id IN %s""" + filters + 'AND l.operating_unit_id= ' + str(
                    operating_unit) + 'GROUP BY l.account_id')
            else:
                sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                    '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                    NULL AS currency_id,\
                    '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                    '' AS partner_name\
                    FROM account_move_line l\
                    LEFT JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN account_move i ON (m.id =i.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    WHERE l.account_id IN %s""" + filters + 'GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace(
            'account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        if operating_unit:
            sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                   m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
                   FROM account_move_line l\
                   JOIN account_move m ON (l.move_id=m.id)\
                   LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                   LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                   JOIN account_journal j ON (l.journal_id=j.id)\
                   JOIN account_account acc ON (l.account_id = acc.id) \
                   WHERE l.account_id IN %s ''' + filters + '''AND l.operating_unit_id= ''' + str(
                operating_unit) + '''GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        else:
            sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
                FROM account_move_line l\
                JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                JOIN account_account acc ON (l.account_id = acc.id) \
                WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)

        return account_res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))

        init_balance = data['form'].get('initial_balance', True)
        operating_unit = data['form'].get('operating_unit')
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]

        accounts = docs if self.model == 'account.account' else self.env[
            'account.account'].search([])
        accounts_res = self.with_context(
            data['form'].get('used_context', {}))._get_account_move_entry(
            accounts, init_balance, sortby, display_account, operating_unit)
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))

        init_balance = data['form'].get('initial_balance', True)
        operating_unit = data['form'].get('operating_unit')
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        accounts = docs if self.model == 'account.account' else self.env[
            'account.account'].search([])
        accounts_res = self.with_context(
            data['form'].get('used_context', {}))._get_account_move_entry(
            accounts, init_balance, sortby, display_account, operating_unit)

        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("General Ledger")
        sheet.set_column(0, 11, 20)

        cell_format = workbook.add_format({'font_size': '12px'})
        bold = workbook.add_format({'bold': True,
                                    'font_size': 10,
                                    })
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                    'border': 1, 'bg_color': '#D3D3D3'})
        txt = workbook.add_format({'font_size': 10, 'bg_color': '#D3D3D3', 'border': 1, 'bold': True})
        txt_column = workbook.add_format({'font_size': 10, 'bg_color': '#dcdcdc', 'bold': True})
        txt_left = workbook.add_format({'align': 'left',
                                        'font_size': 10,
                                        })
        amount = workbook.add_format({'align': 'right',
                                      'font_size': 10,
                                      })

        sheet.merge_range('A2:H2', 'General ledger', head)
        sheet.write('A5', "Journals:", bold)
        sheet.merge_range('B5:H5', str(', '.join([lt or '' for lt in codes])), txt)
        sheet.write('A6', 'Company:', bold)
        if data['form']['company_id'][1]:
            sheet.write('B6', data['form']['company_id'][1], cell_format)
        sheet.write('C6', 'Branch:', bold)
        if data['form']['operating_unit_name']:
            sheet.write('D6', data['form']['operating_unit_name'], cell_format)
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
        sheet.write('B9', 'Date', txt)
        sheet.write('C9', 'JRNL', txt)
        # sheet.write('D9', 'Account', txt)
        sheet.write('D9', 'Partner', txt)
        sheet.write('E9', 'Ref', txt)
        sheet.write('F9', 'Move', txt)
        sheet.write('G9', 'Entry Label', txt)
        sheet.write('H9', 'Debit (SR)', txt)
        sheet.write('I9', 'Credit (SR)', txt)
        sheet.write('J9', 'Balance (SR)', txt)

        row_num = 8
        col_num = 0
        total_debit = 0.0
        total_credit = 0.0
        # logging.info("&&&&&&&&&&&&&&&&& %s" % accounts_res)
        if accounts_res:
            for account in accounts_res:
                sheet.write(row_num + 1, col_num, str(account['code']), txt_column)
                sheet.write(row_num + 1, col_num + 1, str(account['name']), txt_column)
                sheet.write(row_num + 1, col_num + 7, str(round(account['debit'], 2)), bold)
                sheet.write(row_num + 1, col_num + 8, str(round(account['credit'], 2)), bold)
                sheet.write(row_num + 1, col_num + 9, str(round(account['balance'], 2)), bold)
                for line in account['move_lines']:
                    sheet.write(row_num + 2, col_num + 1, str(line['ldate']), txt_left)
                    sheet.write(row_num + 2, col_num + 2, str(line['lcode']), txt_left)
                    # sheet.write(row_num + 2, col_num + 2, account['code'], txt)
                    # sheet.write(row_num + 2, col_num + 3, account['name'], txt)
                    sheet.write(row_num + 2, col_num + 3, str(line['partner_name']), txt_left)
                    if line['lref']:
                        sheet.write(row_num + 2, col_num + 4, str(line['lref']), txt_left)
                    sheet.write(row_num + 2, col_num + 5, str(line['move_name']), txt_left)
                    sheet.write(row_num + 2, col_num + 6, str(line['lname']), txt_left)
                    sheet.write(row_num + 2, col_num + 7, str(round(line['debit'], 2)),
                                txt_left)
                    sheet.write(row_num + 2, col_num + 8, str(round(line['credit'], 2)),
                                txt_left)
                    sheet.write(row_num + 2, col_num + 9, str(round(line['balance'], 2)),
                                txt_left)
                    row_num = row_num + 1
                row_num = row_num + 1
                total_debit += account['debit'] if account['debit'] else 0.0
                total_credit += account['credit'] if account['credit'] else 0.0

            # sheet.write(row_num + 1, col_num + 11, "Total", bold)
            sheet.write(row_num + 1, col_num + 7, str(round(total_debit, 2)), bold)
            sheet.write(row_num + 1, col_num + 8, str(round(total_credit, 2)), bold)
            sheet.write(row_num + 1, col_num + 9,
                        str(round(total_debit - total_credit, 2)), bold)
