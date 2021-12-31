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


class ReportJournal(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_journal_audit'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Journal Report'

    def lines(self, target_move, journal_ids, sort_selection, data, operating_unit):
        if isinstance(journal_ids, int):
            journal_ids = [journal_ids]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        logging.info("******************data %s" % data)
        logging.info("******************%s" % list(query_get_clause))
        params = [tuple(move_state), tuple(journal_ids)] + query_get_clause[2]
        if operating_unit:
            query = 'SELECT "account_move_line".id FROM ' + query_get_clause[
                0] + ', account_move am, account_account acc WHERE "account_move_line".account_id = acc.id AND "account_move_line".operating_unit_id = ' + str(
                operating_unit) + ' AND "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + \
                    query_get_clause[1] + 'ORDER BY '
        else:
            query = 'SELECT "account_move_line".id FROM ' + query_get_clause[
                0] + ', account_move am, account_account acc WHERE "account_move_line".account_id = acc.id AND "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + \
                    query_get_clause[1] + 'ORDER BY '
        if sort_selection == 'date':
            query += '"account_move_line".date'
        else:
            query += 'am.name'
        query += ', "account_move_line".move_id, acc.code'
        self.env.cr.execute(query, tuple(params))
        ids = (x[0] for x in self.env.cr.fetchall())
        return self.env['account.move.line'].browse(ids)

    def _sum_debit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[
            2]
        operating_unit = data['form'].get('operating_unit')
        logging.info("**************************operating_unit %s" % type(operating_unit))
        if operating_unit:
            self.env.cr.execute('SELECT SUM(debit) FROM ' + query_get_clause[
                0] + ', account_move am '
                     'WHERE "account_move_line".move_id=am.id AND "account_move_line".operating_unit_id = ' + str(
                operating_unit) + ' AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' +
                                query_get_clause[1] + ' ',
                                tuple(params))
        else:
            self.env.cr.execute('SELECT SUM(debit) FROM ' + query_get_clause[
                0] + ', account_move am '
                     'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' +
                                query_get_clause[1] + ' ',
                                tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    def _sum_credit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[
            2]
        operating_unit = data['form'].get('operating_unit')
        if operating_unit:
            self.env.cr.execute('SELECT SUM(credit) FROM ' + query_get_clause[
                0] + ', account_move am '
                     'WHERE "account_move_line".move_id=am.id AND "account_move_line".operating_unit_id = ' + str(
                operating_unit) + 'AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' +
                                query_get_clause[1] + ' ',
                                tuple(params))
        else:
            self.env.cr.execute('SELECT SUM(credit) FROM ' + query_get_clause[
                0] + ', account_move am '
                     'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' +
                                query_get_clause[1] + ' ',
                                tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    def _get_taxes(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[
            2]
        operating_unit = data['form'].get('operating_unit')
        if operating_unit:
            query = """
                SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
                FROM account_move_line_account_tax_rel rel, """ + query_get_clause[
                0] + """ 
                LEFT JOIN account_move am ON "account_move_line".move_id = am.id
                WHERE "account_move_line".id = rel.account_move_line_id
                    AND "account_move_line".operating_unit_id = """ + str(operating_unit) + """
                    AND am.state IN %s
                    AND "account_move_line".journal_id IN %s
                    AND """ + query_get_clause[1] + """
               GROUP BY rel.account_tax_id"""
        else:
            query = """
                SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
                FROM account_move_line_account_tax_rel rel, """ + query_get_clause[
                0] + """ 
                LEFT JOIN account_move am ON "account_move_line".move_id = am.id
                WHERE "account_move_line".id = rel.account_move_line_id
                    AND am.state IN %s
                    AND "account_move_line".journal_id IN %s
                    AND """ + query_get_clause[1] + """
               GROUP BY rel.account_tax_id"""
        self.env.cr.execute(query, tuple(params))
        ids = []
        base_amounts = {}
        for row in self.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]] = row[1]

        res = {}
        for tax in self.env['account.tax'].browse(ids):
            if operating_unit:
                self.env.cr.execute(
                    'SELECT sum(debit - credit) FROM ' + query_get_clause[
                        0] + ', account_move am '
                             'WHERE "account_move_line".move_id=am.id AND "account_move_line".operating_unit_id = ' + str(
                        operating_unit) + ' AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' +
                    query_get_clause[1] + ' AND tax_line_id = %s',
                    tuple(params + [tax.id]))
            else:
                self.env.cr.execute(
                    'SELECT sum(debit - credit) FROM ' + query_get_clause[
                        0] + ', account_move am '
                             'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' +
                    query_get_clause[1] + ' AND tax_line_id = %s',
                    tuple(params + [tax.id]))
            res[tax] = {
                'base_amount': base_amounts[tax.id],
                'tax_amount': self.env.cr.fetchone()[0] or 0.0,
            }
            if journal_id.type == 'sale':
                # sales operation are credits
                res[tax]['base_amount'] = res[tax]['base_amount'] * -1
                res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
        return res

    def _get_query_get_clause(self, data):
        return self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        target_move = data['form'].get('target_move', 'all')
        sort_selection = data['form'].get('sort_selection', 'date')
        operating_unit = data['form'].get('operating_unit')

        res = {}
        for journal in data['form']['journal_ids']:
            res[journal] = self.with_context(
                data['form'].get('used_context', {})).lines(target_move,
                                                            journal,
                                                            sort_selection,
                                                            data, operating_unit)
        return {
            'doc_ids': data['form']['journal_ids'],
            'doc_model': self.env['account.journal'],
            'data': data,
            'docs': self.env['account.journal'].browse(
                data['form']['journal_ids']),
            'time': time,
            'lines': res,
            'sum_credit': self._sum_credit,
            'sum_debit': self._sum_debit,
            'get_taxes': self._get_taxes,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        docs = self.env['account.journal'].browse(
            data['form']['journal_ids'])

        sort_selection = data['form'].get('sort_selection', 'date')
        target_move = data['form'].get('target_move', 'all')
        operating_unit = data['form'].get('operating_unit')

        res = {}
        for journal in data['form']['journal_ids']:
            res[journal] = self.with_context(
                data['form'].get('used_context', {})).lines(target_move, journal, sort_selection, data, operating_unit)

        for doc in docs:
            currency_symbol = self.env.user.company_id.currency_id.symbol
            sheet = workbook.add_worksheet(str(doc.name))
            sheet.set_column(0, 8, 20)
            cell_format = workbook.add_format({'font_size': '12px'})
            bold = workbook.add_format({'bold': True,
                                        'font_size': 10,
                                        })
            head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                        'border': 1, 'bg_color': '#D3D3D3'})
            txt = workbook.add_format({'font_size': 10, 'border': 1,'bg_color': '#D3D3D3', 'bold': True})

            txt_left = workbook.add_format({'align': 'left',
                                            'font_size': 10,
                                            })
            amount = workbook.add_format({'align': 'right',
                                          'font_size': 10,
                                          })
            sheet.merge_range('A2:G2', str(doc.name), head)
            sheet.write('A6', 'Company:', bold)
            if data['form']['company_id'][1]:
                sheet.write('B6', data['form']['company_id'][1], cell_format)
            sheet.write('C6', 'Branch:', bold)
            if data['form']['operating_unit_name']:
                sheet.write('D6', data['form']['operating_unit_name'], cell_format)
            sheet.write('A7', 'From:', bold)
            sheet.write('C7', 'To:', bold)
            if data['form'].get('date_from') and data['form'].get('date_to'):
                sheet.write('B7', data['form']['date_from'], cell_format)
                sheet.write('D7', data['form']['date_to'], cell_format)

            sheet.write('E6', 'Entries Sorted By:', bold)
            if data['form'].get('sort_selection') == 'date':
                sheet.write('F6', 'Date', cell_format)
            elif data['form'].get('sort_selection') == 'move_name':
                sheet.write('F6', 'Journal Entry Number', cell_format)

            sheet.write('E7', 'Target Moves:', bold)
            if data['form'].get('target_move') == 'all':
                sheet.write('F7', 'All Entries', cell_format)
            elif data['form'].get('target_move') == 'posted':
                sheet.write('F7', 'All Posted Entries', cell_format)

            sheet.write('A9', 'Move', bold)
            sheet.write('B9', 'Date', bold)
            sheet.write('C9', 'Code', txt)
            sheet.write('D9', 'Account', txt)
            sheet.write('E9', 'Partner', bold)
            sheet.write('F9', 'Label', bold)
            sheet.write('G9', 'Debit (SR)', bold)
            sheet.write('H9', 'Credit (SR)', bold)
            if data['form'].get('amount_currency'):
                sheet.write('I9', 'Currency', bold)

            row_num = 8
            col_num = 0

            for obj in res[doc.id]:
                sheet.write(row_num + 1, col_num,
                            str(obj.move_id.name != '/' and obj.move_id.name or ('*' + str(obj.move_id.id))), txt_left)
                sheet.write(row_num + 1, col_num + 1, str(obj.date), txt_left)
                sheet.write(row_num + 1, col_num + 2, str(obj.account_id.code), txt)
                sheet.write(row_num + 1, col_num + 3, str(obj.account_id.name), txt)
                sheet.write(row_num + 1, col_num + 4, str(
                    obj.sudo().partner_id and obj.sudo().partner_id.name and obj.sudo().partner_id.name[:23] or ''),
                            txt_left)
                sheet.write(row_num + 1, col_num + 5, str(obj.name and obj.name[:35]), txt_left)
                sheet.write(row_num + 1, col_num + 6, str(round(obj.debit, 2)), txt_left)
                sheet.write(row_num + 1, col_num + 7, str(round(obj.credit, 2)), txt_left)
                if data['form']['amount_currency'] and obj.amount_currency:
                    sheet.write(row_num + 1, col_num + 8, str(round(obj.amount_currency, 2)),
                                txt_left)
                row_num = row_num + 1

            # sheet.write(row_num + 2, col_num + 9, "Total", bold)
            sheet.write(row_num + 2, col_num + 6, str(self._sum_debit(data, doc)), txt_left)
            sheet.write(row_num + 2, col_num + 7, str(self._sum_credit(data, doc)), txt_left)
            sheet.write(row_num + 3, col_num, "Tax Declaration", bold)
            sheet.write(row_num + 4, col_num, "Name", bold)
            sheet.write(row_num + 4, col_num + 1, "Base Amount (SR)", bold)
            sheet.write(row_num + 4, col_num + 2, "Tax Amount (SR)", bold)
            taxes = self._get_taxes(data, doc)
            for tax in taxes:
                sheet.write(row_num + 5, col_num, str(tax.name), txt_left)
                sheet.write(row_num + 5, col_num + 1, str(round(taxes[tax]['base_amount'], 2)),
                            txt_left)
                sheet.write(row_num + 5, col_num + 2, str(round(taxes[tax]['tax_amount'], 2)),
                            txt_left)
                row_num = row_num + 1
            # logging.info("*************************** row_num %s" % str(self._get_taxes(data, doc)))
            # logging.info("*************************** objects %s" % res[doc.id])
