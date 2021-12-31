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

from _datetime import datetime
import logging
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTax(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_tax'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Tax Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
        }

    def _sql_from_amls_one(self, options):

        operating_unit = options.get('operating_unit')
        if operating_unit:
            sql = """SELECT "account_move_line".tax_line_id,account.id AS account_id,"account_move_line".move_id,
            move.name,"account_move_line".price_unit,"account_move_line".quantity,move.ref,move.invoice_partner_display_name,account.name AS account,account.code AS code,
            COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0), move.ref
                    FROM %s,account_account AS account,account_move AS move
                    WHERE %s AND "account_move_line".tax_exigible
                    AND "account_move_line".account_id = account.id
                    AND "account_move_line".move_id = move.id
                    AND "account_move_line".operating_unit_id =""" + str(operating_unit) + """
                    GROUP BY "account_move_line".tax_line_id, account.id,account.name,account.code,move.name,"account_move_line".price_unit,
                    "account_move_line".quantity,move.ref,move.invoice_partner_display_name,"account_move_line".move_id, move.ref"""
        else:
            sql = """SELECT "account_move_line".tax_line_id,account.id AS account_id,"account_move_line".move_id,
                    move.name,"account_move_line".price_unit,"account_move_line".quantity,move.ref,move.invoice_partner_display_name,account.name AS account,account.code AS code,
                    COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0),move.ref
                   FROM %s,account_account AS account,account_move AS move
                   WHERE %s AND "account_move_line".tax_exigible
                   AND "account_move_line".account_id = account.id
                   AND "account_move_line".move_id = move.id
                   GROUP BY "account_move_line".tax_line_id, account.id,account.name,account.code,move.name,"account_move_line".price_unit,
                   "account_move_line".quantity,move.ref,move.invoice_partner_display_name,"account_move_line".move_id, move.ref """
        return sql

    def _sql_from_amls_two(self, options):

        operating_unit = options.get('operating_unit')
        if operating_unit:
            sql = """SELECT r.account_tax_id, "account_move_line".account_id,"account_move_line".move_id,COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                    INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                    WHERE %s AND "account_move_line".tax_exigible
                    AND "account_move_line".operating_unit_id =""" + str(operating_unit) + """
                    GROUP BY "account_move_line".account_id,"account_move_line".move_id,r.account_tax_id"""
        else:
            sql = """SELECT r.account_tax_id,"account_move_line".account_id,"account_move_line".move_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                     FROM %s
                     INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                     INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                     WHERE %s AND "account_move_line".tax_exigible GROUP BY "account_move_line".account_id,"account_move_line".move_id,r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes):
        # compute the tax amount
        sql = self._sql_from_amls_one(options)
        tables, where_clause, where_params = self.env[
            'account.move.line']._query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        logging.info("********************results %s" % results)
        # logging.info("********************results %s" % taxes)

        for result in results:
            if result[0] in taxes:
                logging.info("unit_prieceeeee %s" % abs(result[4]))
                val = {
                    'move': result[3],
                    # (tax_amount*100)/percentage_value
                    'base_amount': abs((result[4] * 100) / (taxes[result[0]][0]['amount'])),
                    'tax_amount': abs(result[4]),
                    'total_amount': abs((result[4] * 100) / (taxes[result[0]][0]['amount'])) + abs(result[4]),
                    'ref': result[6],
                    'partner': result[7],
                    'code': result[9],
                    'name': taxes[result[0]][0]['name'],
                    'type': taxes[result[0]][0]['type'],
                }

                taxes[result[0]].append(val)

        # compute the net amount
        sql2 = self._sql_from_amls_two(options)
        query = sql2 % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()

        for result in results:
            if result[0] in taxes:
                # logging.info("********************results %s" % result[0])
                # logging.info("********************results %s" % result[1])
                # taxes[result[0]]['net'] = abs(result[1])
                pass
        # logging.info("********************last taxes id %s" % taxes)
        return taxes

    @api.model
    def get_lines(self, options):
        taxes = {}
        for tax in self.env['account.tax'].search(
                [('type_tax_use', '!=', 'none')]):
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = []
                    val = {'amount': child.amount, 'net': 0, 'name': child.name,
                           'type': tax.type_tax_use, 'partner': '', 'move': '', 'code': '', 'ref': '',
                           'tax_amount': '', 'base_amount': '', 'total_amount': ''}

                    taxes[child.id].append(val)
            else:
                taxes[tax.id] = []
                val = {'amount': tax.amount, 'net': 0, 'name': tax.name, 'code': '', 'ref': '',
                       'type': tax.type_tax_use, 'partner': '', 'move': '',
                       'tax_amount': '', 'base_amount': '', 'total_amount': ''}
                taxes[tax.id].append(val)
        if options['date_from']:
            self.with_context(date_from=options['date_from'],
                              strict_range=True)._compute_from_amls(options,
                                                                    taxes)
        elif options['date_to']:
            self.with_context(date_to=options['date_to'],
                              strict_range=True)._compute_from_amls(options,
                                                                    taxes)
        elif options['date_from'] and options['date_to']:
            self.with_context(date_from=options['date_from'],
                              date_to=options['date_to'],
                              strict_range=True)._compute_from_amls(options,
                                                                    taxes)
        else:
            date_to = str(datetime.today().date())
            self.with_context(date_to=date_to,
                              strict_range=True)._compute_from_amls(options,
                                                                    taxes)

        # groups = dict((tp, []) for tp in ['sale', 'purchase'])
        # for tax in taxes.values():
        #     if tax['tax_amount']:
        #         groups[tax['type']].append(tax)
        # return groups
        return taxes

    def generate_xlsx_report(self, workbook, data, partners):
        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("Tax Report")
        sheet.set_column(0, 7, 20)
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
        sheet.merge_range('A2:D2', 'Tax Report', head)
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

        # sheet.write('A9', 'Name', bold)
        # sheet.write('B9', 'Partner', bold)
        # sheet.write('C9', 'Code', txt)
        # sheet.write('D9', 'Account', txt)
        # sheet.write('E9', 'Ref', bold)
        # sheet.write('F9', 'Net (SR)', bold)
        # sheet.write('G9', 'Tax (SR)', bold)

        sheet.write('A9', 'Name', txt)
        sheet.write('B9', 'Move', txt)
        sheet.write('C9', 'Ref', txt)
        sheet.write('D9', 'Partner', txt)
        sheet.write('E9', 'Code', txt)
        sheet.write('F9', 'Taxable Value (SR)', txt)
        sheet.write('G9', 'Tax Amount (SR)', txt)
        sheet.write('H9', 'Total Amount (SR)', txt)

        lines = self.get_lines(data.get('form'))
        row_num = 8
        col_num = 0
        logging.info("in exxcel sheet %s" % lines)
        if lines:
            sheet.write(row_num + 1, col_num, 'Vat Output', txt)
            row_num = row_num + 1
            base_amount = 0.0
            tax_amount = 0.0
            total_amount = 0.0

            for line in lines:
                for item in lines[line][1:]:
                    logging.info(item)
                    if item['type'] == 'sale':
                        sheet.write(row_num + 1, col_num, str(item.get('name')), txt_left)
                        sheet.write(row_num + 1, col_num + 1, str(item.get('move')), txt_left)
                        sheet.write(row_num + 1, col_num + 2, str(item.get('ref')), txt_left)
                        sheet.write(row_num + 1, col_num + 3, str(item.get('partner')), txt_left)
                        sheet.write(row_num + 1, col_num + 4, str(item.get('code')), txt_left)
                        sheet.write(row_num + 1, col_num + 5, str(round(item.get('base_amount'), 2)), txt_left)
                        sheet.write(row_num + 1, col_num + 6, str(round(item.get('tax_amount'), 2)), txt_left)
                        sheet.write(row_num + 1, col_num + 7, str(round(item.get('total_amount'), 2)), txt_left)
                        base_amount += item.get('base_amount') if item.get('base_amount') else 0.0
                        tax_amount += item.get('tax_amount') if item.get('tax_amount') else 0.0
                        total_amount += item.get('total_amount') if item.get('total_amount') else 0.0
                        row_num = row_num + 1

                    sheet.write(row_num + 1, col_num + 5, str(round(base_amount, 2)), bold)
                    sheet.write(row_num + 1, col_num + 6, str(round(tax_amount, 2)), bold)
                    sheet.write(row_num + 1, col_num + 7, str(round(total_amount, 2)), bold)

            row_num = row_num + 1
            sheet.write(row_num + 1, col_num, 'Vat Input', txt)
            per_base_amount = 0.0
            per_tax_amount = 0.0
            per_total_amount = 0.0
            row_num = row_num + 1
            for line in lines:
                for item in lines[line][1:]:
                    logging.info(item)
                    if item['type'] == 'purchase':
                        sheet.write(row_num + 1, col_num, str(item.get('name')), txt_left)
                        sheet.write(row_num + 1, col_num + 1, str(item.get('move')), txt_left)
                        sheet.write(row_num + 1, col_num + 2, str(item.get('ref')), txt_left)
                        sheet.write(row_num + 1, col_num + 3, str(item.get('partner')), txt_left)
                        sheet.write(row_num + 1, col_num + 4, str(item.get('code')), txt_left)
                        sheet.write(row_num + 1, col_num + 5, str(round(item.get('base_amount'), 2)), txt_left)
                        sheet.write(row_num + 1, col_num + 6, str(round(item.get('tax_amount'), 2)), txt_left)
                        sheet.write(row_num + 1, col_num + 7, str(round(item.get('total_amount'), 2)), txt_left)
                        per_base_amount += item.get('base_amount') if item.get('base_amount') else 0.0
                        per_tax_amount += item.get('tax_amount') if item.get('tax_amount') else 0.0
                        per_total_amount += item.get('total_amount') if item.get('total_amount') else 0.0
                        row_num = row_num + 1

                    sheet.write(row_num + 1, col_num + 5, str(round(per_tax_amount, 2)), bold)
                    sheet.write(row_num + 1, col_num + 6, str(round(per_tax_amount, 2)), bold)
                    sheet.write(row_num + 1, col_num + 7, str(round(per_total_amount, 2)), bold)
