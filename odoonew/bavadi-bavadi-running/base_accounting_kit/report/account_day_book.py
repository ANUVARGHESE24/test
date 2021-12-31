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
from datetime import timedelta, datetime
import logging
from odoo import models, api, _
from odoo.exceptions import UserError


class DayBookPdfReport(models.AbstractModel):
    _name = 'report.base_accounting_kit.day_book_report_template'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Day Book Report'

    def _get_account_move_entry(self, accounts, operating_unit, form_data, pass_date):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        tables, where_clause, where_params = move_line._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        if form_data['target_move'] == 'posted':
            target_move = "AND m.state = 'posted'"
        else:
            target_move = ''
        if operating_unit:
            sql = ('''
                    SELECT l.id AS lid, acc.code as acccode,acc.name as accname, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, 
                    l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                    COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                    m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    JOIN account_account acc ON (l.account_id = acc.id) 
                    WHERE l.operating_unit_id=''' + str(operating_unit) + '''
                    AND l.account_id IN %s  AND l.journal_id IN %s ''' + target_move + ''' AND l.date = %s
                    GROUP BY l.id, l.account_id, l.date,
                         j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name,acc.code
                         ORDER BY l.date DESC
            ''')
        else:
            sql = ('''
                   SELECT l.id AS lid, acc.code as acccode, acc.name as accname, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, 
                   l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                   COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                   m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
                   FROM account_move_line l
                   JOIN account_move m ON (l.move_id=m.id)
                   LEFT JOIN res_currency c ON (l.currency_id=c.id)
                   LEFT JOIN res_partner p ON (l.partner_id=p.id)
                   JOIN account_journal j ON (l.journal_id=j.id)
                   JOIN account_account acc ON (l.account_id = acc.id) 
                   WHERE l.account_id IN %s  AND l.journal_id IN %s ''' + target_move + ''' AND l.date = %s
                   GROUP BY l.id, l.account_id, l.date,
                        j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name,acc.code
                        ORDER BY l.date DESC
                       ''')
        params = (
            tuple(accounts.ids), tuple(form_data['journal_ids']), pass_date)
        cr.execute(sql, params)
        data = cr.dictfetchall()
        res = {}
        debit = credit = balance = 0.00
        # logging.info("PPPPPPPPPPPPPPPPPPPPPPPP%s" % data)
        for line in data:
            debit += line['debit']
            credit += line['credit']
            balance += line['balance']
        res['debit'] = debit
        res['credit'] = credit
        res['balance'] = balance
        res['lines'] = data
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        form_data = data['form']
        operating_unit = data['form'].get('operating_unit')
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        active_acc = data['form']['account_ids']
        accounts = self.env['account.account'].search(
            [('id', 'in', active_acc)]) if data['form']['account_ids'] else \
            self.env['account.account'].search([])

        date_start = datetime.strptime(form_data['date_from'],
                                       '%Y-%m-%d').date()
        date_end = datetime.strptime(form_data['date_to'], '%Y-%m-%d').date()
        days = date_end - date_start
        dates = []
        record = []
        for i in range(days.days + 1):
            dates.append(date_start + timedelta(days=i))
        for head in dates:
            pass_date = str(head)
            accounts_res = self.with_context(
                data['form'].get('used_context', {}))._get_account_move_entry(
                accounts, operating_unit, form_data, pass_date)
            if accounts_res['lines']:
                record.append({
                    'date': head,
                    'debit': accounts_res['debit'],
                    'credit': accounts_res['credit'],
                    'balance': accounts_res['balance'],
                    'child_lines': accounts_res['lines']
                })
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': record,
            'print_journal': codes,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        form_data = data['form']
        operating_unit = data['form'].get('operating_unit')
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        active_acc = data['form']['account_ids']
        accounts = self.env['account.account'].search(
            [('id', 'in', active_acc)]) if data['form']['account_ids'] else \
            self.env['account.account'].search([])

        date_start = datetime.strptime(form_data['date_from'],
                                       '%Y-%m-%d').date()
        date_end = datetime.strptime(form_data['date_to'], '%Y-%m-%d').date()
        days = date_end - date_start
        dates = []
        record = []
        for i in range(days.days + 1):
            dates.append(date_start + timedelta(days=i))
        for head in dates:
            pass_date = str(head)
            accounts_res = self.with_context(
                data['form'].get('used_context', {}))._get_account_move_entry(
                accounts, operating_unit, form_data, pass_date)
            if accounts_res['lines']:
                record.append({
                    'date': head,
                    'debit': accounts_res['debit'],
                    'credit': accounts_res['credit'],
                    'balance': accounts_res['balance'],
                    'child_lines': accounts_res['lines']
                })
        data = data['form']
        print_journal = codes
        # logging.info("*************************** print_journal %s" % print_journal)
        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("Day Book Report")
        sheet.set_column(0, 9, 20)
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
        # logging.info("*************************** objects %s" % data)
        sheet.merge_range('A2:H2', 'Day Book Report', head)
        sheet.write('A5', 'Journal:', bold)
        if print_journal:
            sheet.merge_range('B5:H5', ', '.join([lt or '' for lt in print_journal]), txt)
        sheet.write('A6', 'Company:', bold)
        sheet.write('B6', self.env.company.name, cell_format)
        sheet.write('C6', 'Branch:', bold)
        if data['operating_unit_name']:
            sheet.write('D6', data['operating_unit_name'], cell_format)
        sheet.write('A7', 'From:', bold)
        sheet.write('C7', 'To:', bold)
        # logging.info("*************************** objects %s" % data)
        if data['date_from'] and data['date_to']:
            sheet.write('B7', data['date_from'], cell_format)
            sheet.write('D7', data['date_to'], cell_format)

        sheet.write('E6', 'Target Moves:', bold)
        if data['target_move'] == 'all':
            sheet.write('F6', 'All Entries', cell_format)
        elif data['target_move'] == 'posted':
            sheet.write('F6', 'All Posted Entries', cell_format)

        sheet.write('A9', 'Date', bold)
        sheet.write('B9', 'JRNL', bold)
        sheet.write('C9', 'Code', txt)
        sheet.write('D9', 'Account', txt)
        sheet.write('E9', 'Partner', bold)
        sheet.write('F9', 'Ref', bold)
        sheet.write('G9', 'Move', bold)
        sheet.write('H9', 'Entry Label', bold)
        sheet.write('I9', 'Debit (SR)', bold)
        sheet.write('J9', 'Credit (SR)', bold)
        sheet.write('K9', 'Balance (SR)', bold)
        # sheet.write('J9', 'Move', bold)

        row_num = 8
        col_num = 0
        total_debit = 0.0
        total_credit = 0.0
        # logging.info("*************************** accounts %s" % accounts)
        if record:
            for i in record:
                sheet.write(row_num + 1, col_num, str(i['date']), bold)
                sheet.write(row_num + 1, col_num + 8, str(round(i['debit'], 2)), bold)
                sheet.write(row_num + 1, col_num + 9, str(round(i['credit'], 2)), bold)
                sheet.write(row_num + 1, col_num + 10, str(round(i['balance'], 2)), bold)
                # total_debit += i['debit'] if i['debit'] else 0.0
                # total_credit += i['credit'] if i['credit'] else 0.0
                row_num = row_num + 1
                for line in i['child_lines']:
                    sheet.write(row_num + 1, col_num, str(line['ldate']), txt_left)
                    sheet.write(row_num + 1, col_num + 1, line['lcode'], txt_left)
                    sheet.write(row_num + 1, col_num + 2, str(line['acccode']), txt)
                    sheet.write(row_num + 1, col_num + 3, line['accname'], txt)
                    sheet.write(row_num + 1, col_num + 4, line['partner_name'], txt_left)
                    if line['lref']:
                        sheet.write(row_num + 1, col_num + 5, line['lref'], txt_left)
                    sheet.write(row_num + 1, col_num + 6, line['move_name'], txt_left)
                    sheet.write(row_num + 1, col_num + 7, line['lname'], txt_left)
                    sheet.write(row_num + 1, col_num + 8, str(line['debit']), txt_left)
                    sheet.write(row_num + 1, col_num + 9, str(line['credit']), txt_left)
                    sheet.write(row_num + 1, col_num + 10, str(line['balance']), txt_left)
                    row_num = row_num + 1
                    # if line['amount_currency']:
                    #     sheet.write(row_num + 1, col_num + 8, line['amount_currency'], txt_left)
                # row_num = row_num + 1
            # sheet.write(row_num + 1, col_num + 2, "Total", bold)
            # sheet.write(row_num + 1, col_num + 4, str(round(total_debit, 2)) + str(currency_symbol), bold)
            # sheet.write(row_num + 1, col_num + 6, str(round(total_credit, 2)) + str(currency_symbol), bold)
            # sheet.write(row_num + 1, col_num + 8,
            #             str(round(total_debit, 2) - round(total_credit, 2)) + str(currency_symbol), bold)
        # logging.info("*************************** objects %s" % accounts)
