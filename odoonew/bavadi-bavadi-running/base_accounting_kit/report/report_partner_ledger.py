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


class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_partnerledger'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Partner Ledger Report'

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        operating_unit = data['form'].get('operating_unit')
        if operating_unit:
            params = [partner.id, tuple(data['computed']['move_state']),
                      tuple(data['computed']['account_ids'])] + \
                     query_get_data[2]
            query = """
                SELECT "account_move_line".id,"account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit,
                "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
                FROM """ + query_get_data[0] + """
                LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
                LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
                LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
                LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
                WHERE "account_move_line".partner_id = %s
                    AND "account_move_line".operating_unit_id =""" + str(operating_unit) + """
                    AND m.state IN %s
                    AND "account_move_line".account_id IN %s AND """ + \
                    query_get_data[1] + reconcile_clause + """
                    ORDER BY "account_move_line".date"""
        else:
            params = [partner.id, tuple(data['computed']['move_state']),
                      tuple(data['computed']['account_ids'])] + \
                     query_get_data[2]
            query = """
                SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
                FROM """ + query_get_data[0] + """
                LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
                LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
                LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
                LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
                WHERE "account_move_line".partner_id = %s
                    AND m.state IN %s
                    AND "account_move_line".account_id IN %s AND """ + \
                    query_get_data[1] + reconcile_clause + """
                    ORDER BY "account_move_line".date"""

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        # logging.info("query_get_data[0] %s" % (query_get_data[0]))
        # logging.info("query_get_data[1] %s" % (query_get_data[1]))
        # logging.info(res)
        # logging.info("*************************************************************")
        # logging.info("%s" % (data['form'].get('operating_unit')))
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        operating_unit = data['form'].get('operating_unit')
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        if operating_unit:
            query = """SELECT sum(""" + field + """)
                    FROM """ + query_get_data[0] + """, account_move AS m
                    WHERE "account_move_line".partner_id = %s
                        AND "account_move_line".operating_unit_id = """ + str(operating_unit) + """
                        AND m.id = "account_move_line".move_id
                        AND m.state IN %s
                        AND account_id IN %s
                        AND """ + query_get_data[1] + reconcile_clause
        else:
            query = """SELECT sum(""" + field + """)
                   FROM """ + query_get_data[0] + """, account_move AS m
                   WHERE "account_move_line".partner_id = %s
                       AND m.id = "account_move_line".move_id
                       AND m.state IN %s
                       AND account_id IN %s
                       AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        data['computed'] = {}
        operating_unit = data['form'].get('operating_unit')
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""",
                            (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in
                                           self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        if operating_unit:
            query = """
                SELECT DISTINCT "account_move_line".partner_id
                FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                WHERE "account_move_line".partner_id IS NOT NULL
                    AND "account_move_line".account_id = account.id
                    AND am.id = "account_move_line".move_id
                    AND am.state IN %s
                    AND "account_move_line".account_id IN %s
                    AND "account_move_line".operating_unit_id = """ + str(operating_unit) + """
                    AND NOT account.deprecated
                    AND """ + query_get_data[1] + reconcile_clause
        else:
            query = """
               SELECT DISTINCT "account_move_line".partner_id
               FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
               WHERE "account_move_line".partner_id IS NOT NULL
                   AND "account_move_line".account_id = account.id
                   AND am.id = "account_move_line".move_id
                   AND am.state IN %s
                   AND "account_move_line".account_id IN %s
                   AND NOT account.deprecated
                   AND """ + query_get_data[1] + reconcile_clause

        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        data['computed'] = {}
        operating_unit = data['form'].get('operating_unit')
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
                    SELECT a.id
                    FROM account_account a
                    WHERE a.internal_type IN %s
                    AND NOT a.deprecated""",
                            (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in
                                           self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        if operating_unit:
            query = """
                        SELECT DISTINCT "account_move_line".partner_id
                        FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                        WHERE "account_move_line".partner_id IS NOT NULL
                            AND "account_move_line".account_id = account.id
                            AND am.id = "account_move_line".move_id
                            AND am.state IN %s
                            AND "account_move_line".account_id IN %s
                            AND "account_move_line".operating_unit_id = """ + str(operating_unit) + """
                            AND NOT account.deprecated
                            AND """ + query_get_data[1] + reconcile_clause
        else:
            query = """
                       SELECT DISTINCT "account_move_line".partner_id
                       FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                       WHERE "account_move_line".partner_id IS NOT NULL
                           AND "account_move_line".account_id = account.id
                           AND am.id = "account_move_line".move_id
                           AND am.state IN %s
                           AND "account_move_line".account_id IN %s
                           AND NOT account.deprecated
                           AND """ + query_get_data[1] + reconcile_clause

        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("Partner Ledger")
        sheet.set_column(0, 7, 20)
        cell_format = workbook.add_format({'font_size': '12px'})
        bold = workbook.add_format({'bold': True,
                                    'font_size': 10,
                                    })
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                    'border': 1, 'bg_color': '#D3D3D3'})
        txt = workbook.add_format({'border': 1, 'font_size': 10})

        txt_left = workbook.add_format({'align': 'left',
                                        'font_size': 10,
                                        })
        amount = workbook.add_format({'align': 'right',
                                      'font_size': 10,
                                      })
        sheet.merge_range('A2:H2', 'Partner ledger', head)
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

        sheet.write('E6', 'Target Moves:', bold)
        if data['form']['target_move'] == 'all':
            sheet.write('F6', 'All Entries', cell_format)
        elif data['form']['target_move'] == 'posted':
            sheet.write('F6', 'All Posted Entries', cell_format)

        sheet.write('A9', 'Date', bold)
        sheet.write('B9', 'JRNL', bold)
        sheet.write('C9', 'Code', bold)
        sheet.write('D9', 'Account', bold)
        sheet.write('E9', 'Ref', bold)
        sheet.write('F9', 'Debit (SR)', bold)
        sheet.write('G9', 'Credit (SR)', bold)
        sheet.write('H9', 'Balance (SR)', bold)
        if data['form']['amount_currency']:
            sheet.write('I9', 'Currency', bold)

        row_num = 8
        col_num = 0
        total_debit = 0.0
        total_credit = 0.0
        lines = self._lines
        if partners:
            for o in partners:
                sheet.write(row_num + 1, col_num, str(o.ref or "") + "-" + str(o.name or ""), bold)
                sheet.write(row_num + 1, col_num + 5, str(self._sum_partner(data, o, 'debit')) ,
                            bold)
                sheet.write(row_num + 1, col_num + 6, str(self._sum_partner(data, o, 'credit')),
                            bold)
                sheet.write(row_num + 1, col_num + 7,
                            str(self._sum_partner(data, o, 'debit - credit')) , bold)
                for line in lines(data, o):
                    # logging.info("*********************%s" % line)
                    sheet.write(row_num + 2, col_num, str(line['date']), txt_left)
                    sheet.write(row_num + 2, col_num + 1, str(line['code']), txt_left)
                    sheet.write(row_num + 2, col_num + 2, str(line['a_code']), txt_left)
                    sheet.write(row_num + 2, col_num + 3, str(line['a_name']), txt_left)
                    sheet.write(row_num + 2, col_num + 4, str(line['displayed_name']), txt_left)
                    sheet.write(row_num + 2, col_num + 5, str(round(line['debit'], 2)), txt_left)
                    sheet.write(row_num + 2, col_num + 6, str(round(line['credit'], 2)),
                                txt_left)
                    sheet.write(row_num + 2, col_num + 7, str(round(line['progress'], 2)),
                                txt_left)
                    if line['currency_id']:
                        sheet.write(row_num + 2, col_num + 8, str(line['currency_id']), txt_left)
                    # sheet.write(row_num + 2, col_num + 17, str(line['balance']) + str(currency_symbol), amount)
                    row_num = row_num + 1
                row_num = row_num + 1
                total_debit += line['debit'] if line['debit'] else 0.0
                total_credit += line['credit'] if line['credit'] else 0.0

            # sheet.write(row_num + 1, col_num + 7, "Total", bold)
            sheet.write(row_num + 1, col_num + 5, str(round(total_debit, 2)), bold)
            sheet.write(row_num + 1, col_num + 6, str(round(total_credit, 2)) , bold)
            sheet.write(row_num + 1, col_num + 7,
                        str(round(total_debit - total_credit, 2)), bold)
