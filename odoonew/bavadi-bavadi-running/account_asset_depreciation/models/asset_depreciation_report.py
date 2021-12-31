from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging


class AccountAssetDepreciationReport(models.AbstractModel):
    _name = 'report.account_asset_depreciation.depreciation_report_pdf'
    _inherit = "report.report_xlsx.abstract"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        category = data['form']['category']
        lst_end_year = data['form']['lst_end_year']

        self.model = self.env.context.get('active_model')

        assets = self.env['account.asset.asset'].search(
            [('depreciation_line_ids.depreciation_date', '>=', date_from), ('state', 'not in', ['draft']),
             ('depreciation_line_ids.depreciation_date', '<=', date_to), ('category_id', 'in', category)])
        good_assets = []
        total_value = 0
        total_ly_amount = 0
        total_cy_amount = 0
        total_m_depreciation = 0
        total_sp_amount = 0
        total_remaining = 0
        total_d_value = 0

        for a in assets:
            lst_year = self.env['account.asset.depreciation.line'].search(
                [('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '<=', lst_end_year)])
            lst_year_amount = 0
            c_year = self.env['account.asset.depreciation.line'].search(
                [('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '>', lst_end_year),
                 ('depreciation_date', '<=', date_to)])
            c_year_amount = 0
            s_period = self.env['account.asset.depreciation.line'].search(
                [('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '>=', date_from),
                 ('depreciation_date', '<=', date_to)])
            s_period_amount = 0
            total_value += a.value

            for l in lst_year:
                lst_year_amount += l.amount
                a['lst_year_amount'] = lst_year_amount
            total_ly_amount += lst_year_amount

            for c in c_year:
                c_year_amount += c.amount
                a['c_year_amount'] = c_year_amount
            total_cy_amount += c_year_amount

            for s in s_period:
                s_period_amount += s.amount
                a['s_period_amount'] = s_period_amount
                a['s_remaining_value'] = s.remaining_value
                a['s_depreciated_value'] = s.depreciated_value
            total_d_value += s.depreciated_value
            total_sp_amount += s_period_amount
            total_remaining += s.remaining_value

            have_good_lines = self.env['account.asset.depreciation.line'].search(
                [('asset_id', '=', a.id), ('move_check', '=', True)])
            if have_good_lines:
                good_assets.append(a)

        return {
            'names': good_assets,
            'total_m_depreciation': float(total_m_depreciation),
            'total_cy_amount': float(total_cy_amount),
            'total_ly_amount': float(total_ly_amount),
            'total_sp_amount': float(total_sp_amount),
            'total_d_value': float(total_d_value),
            'total_remaining': float(total_remaining),
            'currency_id': self.env.ref('base.main_company').currency_id,
            'total_value': float(total_value),
            'categories': category,
            'date_from': date_from,
            'date_to': date_to,
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': self.env[self.model].browse(self.env.context.get('active_ids', [])),

        }

    def generate_xlsx_report(self, workbook, data, partners):
        report_values = self._get_report_values(docids=None, data=data)
        good_assets = report_values['names']
        total_m_depreciation = report_values['total_m_depreciation']
        total_cy_amount = report_values['total_cy_amount']
        total_ly_amount = report_values['total_ly_amount']
        total_sp_amount = report_values['total_sp_amount']
        total_d_value = report_values['total_d_value']
        total_remaining = report_values['total_remaining']
        total_value = report_values['total_value']
        docs = report_values['docs']
        # if not data.get('form') or not self.env.context.get('active_model'):
        #     raise UserError(_("Form content is missing, this report cannot be printed."))
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        category = data['form']['category']
        lst_end_year = data['form']['lst_end_year']
        codes = [category.name for category in
                 self.env['account.asset.category'].search(
                     [('id', 'in', data['form']['category'])])]
        # self.model = self.env.context.get('active_model')
        #
        # assets = self.env['account.asset.asset'].search(
        #     [('depreciation_line_ids.depreciation_date', '>=', date_from), ('state', 'not in', ['draft']),
        #      ('depreciation_line_ids.depreciation_date', '<=', date_to), ('category_id', 'in', category)])
        # good_assets = []
        # total_value = 0
        # total_ly_amount = 0
        # total_cy_amount = 0
        # total_m_depreciation = 0
        # total_sp_amount = 0
        # total_remaining = 0
        # total_d_value = 0
        #
        # for a in assets:
        #     lst_year = self.env['account.asset.depreciation.line'].search(
        #         [('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '<=', lst_end_year)])
        #     lst_year_amount = 0
        #     c_year = self.env['account.asset.depreciation.line'].search(
        #         [('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '>', lst_end_year),
        #          ('depreciation_date', '<=', date_to)])
        #     c_year_amount = 0
        #     s_period = self.env['account.asset.depreciation.line'].search(
        #         [('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '>=', date_from),
        #          ('depreciation_date', '<=', date_to)])
        #     s_period_amount = 0
        #     total_value += a.value
        #
        #     for l in lst_year:
        #         lst_year_amount += l.amount
        #         a['lst_year_amount'] = lst_year_amount
        #     total_ly_amount += lst_year_amount
        #
        #     for c in c_year:
        #         c_year_amount += c.amount
        #         a['c_year_amount'] = c_year_amount
        #     total_cy_amount += c_year_amount
        #
        #     for s in s_period:
        #         s_period_amount += s.amount
        #         a['s_period_amount'] = s_period_amount
        #         a['s_remaining_value'] = s.remaining_value
        #         a['s_depreciated_value'] = s.depreciated_value
        #     total_d_value += s.depreciated_value
        #     total_sp_amount += s_period_amount
        #     total_remaining += s.remaining_value
        #
        #     have_good_lines = self.env['account.asset.depreciation.line'].search(
        #         [('asset_id', '=', a.id), ('move_check', '=', True)])
        #     if have_good_lines:
        #         good_assets.append(a)

        data = data['form']
        # docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        currency_symbol = self.env.user.company_id.currency_id.symbol

        sheet = workbook.add_worksheet("Asset Depreciation Report")
        sheet.set_column(0, 13, 20)
        cell_format = workbook.add_format({'font_size': '12px'})
        bold = workbook.add_format({'bold': True,
                                    'font_size': 10,
                                    })
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                    'border': 1, 'bg_color': '#D3D3D3'})
        txt = workbook.add_format({'font_size': 10})

        txt_left = workbook.add_format({'align': 'left',
                                        'font_size': 10,
                                        })

        sheet.merge_range('A2:I2', 'Assets Depreciation', head)
        sheet.write('A5', 'Asset categories:', bold)
        sheet.merge_range('B5:D5', ', '.join([lt or '' for lt in codes]), cell_format)
        sheet.write('A6', 'Company:', bold)
        sheet.write('B6', self.env.company.name, cell_format)
        sheet.write('A7', 'From:', bold)
        sheet.write('C7', 'To:', bold)

        if date_from and date_to:
            sheet.write('B7', date_from, cell_format)
            sheet.write('D7', date_to, cell_format)

        sheet.write('A9', '#', bold)
        sheet.write('B9', 'Reference', bold)
        sheet.write('C9', 'Asset', bold)
        sheet.write('D9', 'Date', bold)
        sheet.write('E9', 'Asset account', bold)
        sheet.write('F9', 'Term (months)', bold)
        sheet.write('G9', 'Annual percentage', bold)
        sheet.write('H9', 'Monthly depreciation (SR)', bold)
        sheet.write('I9', 'Gross Value (SR)', bold)
        sheet.write('J9', 'At starting year (SR)', bold)
        sheet.write('K9', 'Accumulated on last years (SR)', bold)
        sheet.write('L9', 'Value Residual (SR)', bold)
        sheet.write('M9', 'Selected period depreciation (SR)', bold)
        sheet.write('N9', 'Total depreciated (SR)', bold)

        row_num = 8
        col_num = 0

        index = 1
        for n in good_assets:
            sheet.write(row_num + 1, col_num, str(index), txt_left)
            sheet.write(row_num + 1, col_num + 1, n.code, txt_left)
            sheet.write(row_num + 1, col_num + 2, n.name, txt_left)
            sheet.write(row_num + 1, col_num + 3, str(n.date), txt_left)
            sheet.write(row_num + 1, col_num + 4, n.category_id.account_asset_id.code, txt_left)
            sheet.write(row_num + 1, col_num + 5, n.months, txt_left)
            sheet.write(row_num + 1, col_num + 6, n.peryear_depreciation, txt_left)
            sheet.write(row_num + 1, col_num + 7, str(n.monthly_depreciation), txt_left)
            sheet.write(row_num + 1, col_num + 8, str(n.value), txt_left)
            sheet.write(row_num + 1, col_num + 9, str(n.c_year_amount), txt_left)
            sheet.write(row_num + 1, col_num + 10, str(n.lst_year_amount), txt_left)
            sheet.write(row_num + 1, col_num + 11, str(n.s_remaining_value), txt_left)
            sheet.write(row_num + 1, col_num + 12, str(n.s_period_amount), txt_left)
            sheet.write(row_num + 1, col_num + 13, str(n.s_depreciated_value), txt_left)

            row_num = row_num + 1
            index += 1
        sheet.write(row_num + 1, col_num + 8, str(float(total_value)), bold)
        sheet.write(row_num + 1, col_num + 9, str(float(total_cy_amount)) , bold)
        sheet.write(row_num + 1, col_num + 10, str(float(total_ly_amount)) , bold)
        sheet.write(row_num + 1, col_num + 11, str(float(total_remaining)) , bold)
        sheet.write(row_num + 1, col_num + 12, str(float(total_sp_amount)) , bold)
        sheet.write(row_num + 1, col_num + 13, str(float(total_d_value)) , bold)
