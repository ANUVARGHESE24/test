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
from datetime import datetime
import logging
from dateutil.relativedelta import relativedelta

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ReportAgedPartnerBalance(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_agedpartnerbalance'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Aged Partner Balance Report'

    def _get_partner_move_lines(self, account_type, date_from, target_move,
                                data):
        # This method can receive the context key 'include_nullified_amount' {Boolean}
        # Do an invoice and a payment and unreconcile. The amount will be nullified
        # By default, the partner wouldn't appear in this report.
        # The context key allow it to appear
        # In case of a period_length of 30 days as of 2019-02-08, we want the following periods:
        # Name       Stop         Start
        # 1 - 30   : 2019-02-07 - 2019-01-09
        # 31 - 60  : 2019-01-08 - 2018-12-10
        # 61 - 90  : 2018-12-09 - 2018-11-10
        # 91 - 120 : 2018-11-09 - 2018-10-11
        # +120     : 2018-10-10
        period_length = data['form'][
            'period_length']
        operating_unit = data['form'][
            'operating_unit']
        periods = {}
        start = datetime.strptime(date_from, "%Y-%m-%d")
        date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5 - (i + 1)) * period_length + 1) + '-' + str(
                (5 - i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        cr = self.env.cr
        user_company = self.env.company
        user_currency = user_company.currency_id
        ResCurrency = self.env['res.currency'].with_context(date=date_from)
        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        # build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute(
            'SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where max_date > %s',
            (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, tuple(company_ids))
        if operating_unit:
            query = '''
                SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
                FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
                WHERE (l.account_id = account_account.id)
                    AND (l.move_id = am.id)
                    AND (l.operating_unit_id = ''' + str(operating_unit) + ''')
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND ''' + reconciliation_clause + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                ORDER BY UPPER(res_partner.name)'''
        else:
            query = '''
               SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
               FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
               WHERE (l.account_id = account_account.id)
                   AND (l.move_id = am.id)
                   AND (am.state IN %s)
                   AND (account_account.internal_type IN %s)
                   AND ''' + reconciliation_clause + '''
                   AND (l.date <= %s)
                   AND l.company_id IN %s
               ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if
                       partner['partner_id']]
        lines = dict(
            (partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        if operating_unit:
            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (l.operating_unit_id = ''' + str(operating_unit) + ''')
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND (COALESCE(l.date_maturity,l.date) >= %s)\
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
        else:
            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND (COALESCE(l.date_maturity,l.date) >= %s)\
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''

        cr.execute(query, (
            tuple(move_state), tuple(account_type), date_from,
            tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = ResCurrency._compute(line.company_id.currency_id,
                                               user_currency, line.balance)
            if user_currency.is_zero(line_amount):
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    line_amount += ResCurrency._compute(
                        partial_line.company_id.currency_id, user_currency,
                        partial_line.amount)
            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    line_amount -= ResCurrency._compute(
                        partial_line.company_id.currency_id, user_currency,
                        partial_line.amount)
            if not self.env.company.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })
            # logging.info("############## %s" % line)
        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (
                tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (
                    periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))
            if operating_unit:
                query = '''SELECT l.id
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                            AND (l.operating_unit_id = ''' + str(operating_unit) + ''')
                            AND (am.state IN %s)
                            AND (account_account.internal_type IN %s)
                            AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                            AND ''' + dates_query + '''
                        AND (l.date <= %s)
                        AND l.company_id IN %s'''
            else:
                query = '''SELECT l.id
                       FROM account_move_line AS l, account_account, account_move am
                       WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                           AND (am.state IN %s)
                           AND (account_account.internal_type IN %s)
                           AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                           AND ''' + dates_query + '''
                       AND (l.date <= %s)
                       AND l.company_id IN %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = ResCurrency._compute(line.company_id.currency_id,
                                                   user_currency, line.balance)
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount += ResCurrency._compute(
                            partial_line.company_id.currency_id, user_currency,
                            partial_line.amount)
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount -= ResCurrency._compute(
                            partial_line.company_id.currency_id, user_currency,
                            partial_line.amount)

                if not self.env.company.currency_id.is_zero(
                        line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                    })
            history.append(partners_amount)

        for partner in partners:
            # logging.info("***************%s" % partner)
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner[
                'partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'],
                                 precision_rounding=self.env.company.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)],
                                     precision_rounding=self.env.company.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum(
                [values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(
                    partner['partner_id'])
                values['name'] = browsed_partner.name and len(
                    browsed_partner.name) >= 45 and browsed_partner.name[
                                                    0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (
                    self._context.get('include_nullified_amount') and lines[
                partner['partner_id']]):
                res.append(values)

        return res, total, lines

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get(
                'active_model') or not self.env.context.get('active_id'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        movelines, total, dummy = self._get_partner_move_lines(account_type,
                                                               date_from,
                                                               target_move,
                                                               data)
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
        }

    def generate_xlsx_report(self, workbook, data, partners):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        total = []
        model = self.env.context.get('active_model')

        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        movelines, total, dummy = self._get_partner_move_lines(account_type,
                                                               date_from,
                                                               target_move,
                                                               data)

        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("Aged Partner Balance")
        sheet.set_column(0, 7, 20)
        cell_format = workbook.add_format({'font_size': '12px'})
        bold = workbook.add_format({'bold': True,
                                    'font_size': 10,
                                    })
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                    'border': 1, 'bg_color': '#D3D3D3'})
        txt = workbook.add_format({'border': 1,'font_size': 10})

        txt_left = workbook.add_format({'align': 'left',
                                        'font_size': 10,
                                        })
        amount = workbook.add_format({'align': 'right',
                                      'font_size': 10,
                                      })
        sheet.merge_range('A2:G2', 'Aged Partner Balance', head)
        sheet.write('A6', 'Company:', bold)
        if data['form']['company_id'][1]:
            sheet.write('B6', data['form']['company_id'][1], cell_format)
        sheet.write('C6', 'Branch:', bold)
        if data['form']['operating_unit_name']:
            sheet.write('D6', data['form']['operating_unit_name'], cell_format)
        sheet.write('A7', 'Start Date::', bold)
        sheet.write('C7', 'Period Length (days):', bold)
        if data['form']['date_from'] and data['form']['period_length']:
            sheet.write('B7', data['form']['date_from'], cell_format)
            sheet.write('D7', data['form']['period_length'], txt_left)

        sheet.write('E6', 'Target Moves:', bold)
        if data['form']['target_move'] == 'all':
            sheet.write('F6', 'All Entries', cell_format)
        elif data['form']['target_move'] == 'posted':
            sheet.write('F6', 'All Posted Entries', cell_format)

        sheet.write('E7', 'Partners:', bold)
        if data['form']['result_selection'] == 'customer':
            sheet.write('F7', 'Receivable Accounts', cell_format)
        elif data['form']['result_selection'] == 'supplier':
            sheet.write('F7', 'Payable Accounts', cell_format)
        elif data['form']['result_selection'] == 'customer_supplier':
            sheet.write('F7', 'Receivable and Payable Accounts', cell_format)

        # sheet.write('A9', 'Code', bold)
        # sheet.write('B9', 'Account', bold)
        sheet.write('A9', 'Partners', bold)
        sheet.write('B9', 'Not due', bold)
        sheet.write('C9', data['form']['4']['name'], bold)
        sheet.write('D9', data['form']['3']['name'], bold)
        sheet.write('E9', data['form']['2']['name'], bold)
        sheet.write('F9', data['form']['1']['name'], bold)
        sheet.write('G9', data['form']['0']['name'], bold)
        sheet.write('H9', 'Total (SR)', bold)

        row_num = 8
        col_num = 0
        # logging.info("************************** %s" % dummy)
        if movelines:
            sheet.write(row_num + 1, col_num, "Account Total", bold)
            sheet.write(row_num + 1, col_num + 1, str(round(total[6], 2)), bold)
            sheet.write(row_num + 1, col_num + 2, str(round(total[4], 2)), bold)
            sheet.write(row_num + 1, col_num + 3, str(round(total[3], 2)), bold)
            sheet.write(row_num + 1, col_num + 4, str(round(total[2], 2)), bold)
            sheet.write(row_num + 1, col_num + 5, str(round(total[1], 2)), bold)
            sheet.write(row_num + 1, col_num + 6, str(round(total[0], 2)), bold)
            sheet.write(row_num + 1, col_num + 7, str(round(total[5], 2)), bold)
            # row_num = row_num + 1
            for partner in movelines:
                # sheet.write(row_num + 2, col_num , str(partner['name']), txt_left)
                # sheet.write(row_num + 2, col_num + 1, str(partner['direction']), txt_left)
                sheet.write(row_num + 2, col_num, str(partner['name']), txt_left)
                sheet.write(row_num + 2, col_num + 1, str(partner['direction']), txt_left)
                sheet.write(row_num + 2, col_num + 2, str(round(partner['4'], 2)), txt_left)
                sheet.write(row_num + 2, col_num + 3, str(round(partner['3'], 2)), txt_left)
                sheet.write(row_num + 2, col_num + 4, str(round(partner['2'], 2)), txt_left)
                sheet.write(row_num + 2, col_num + 5, str(round(partner['1'], 2)), txt_left)
                sheet.write(row_num + 2, col_num + 6, str(round(partner['0'], 2)), txt_left)
                sheet.write(row_num + 2, col_num + 7, str(round(partner['total'], 2)), txt_left)
                row_num = row_num + 1
        # row_num = row_num + 1
        # total_debit += line['debit'] if line['debit'] else 0.0
        # total_credit += line['credit'] if line['credit'] else 0.0
        #
        # sheet.write(row_num + 1, col_num + 7, "Total", bold)
        # sheet.write(row_num + 1, col_num + 9, str(round(total_debit, 2)) + str(currency_symbol), bold)
        # sheet.write(row_num + 1, col_num + 11, str(round(total_credit, 2)) + str(currency_symbol), bold)
        # sheet.write(row_num + 1, col_num + 13,
        #         str(round(total_debit - total_credit, 2)) + str(currency_symbol), bold)
