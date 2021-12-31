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

from odoo import models, fields
from odoo.tools.misc import get_lang


class AccountTaxReport(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.tax.report'
    _description = 'Tax Report'

    # @pk custom field for branch filter
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit')

    def _print_report(self, data):
        data['form'].update({
            'operating_unit': self.operating_unit.id,
            'operating_unit_name': self.operating_unit.name
        })
        return self.env.ref(
            'base_accounting_kit.action_report_account_tax').with_context(
            landscape=True).report_action(
            self, data=data)

    def get_xlsx_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        data['form'].update({
            'operating_unit': self.operating_unit.id,
            'operating_unit_name': self.operating_unit.name
        })
        self.env.ref('base_accounting_kit.action_report_account_tax_excel').report_file = "Tax_Report"
        return self.env.ref('base_accounting_kit.action_report_account_tax_excel').report_action(self, data=data)
