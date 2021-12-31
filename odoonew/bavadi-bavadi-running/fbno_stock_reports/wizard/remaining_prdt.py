# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RemainingProduct(models.TransientModel):
    _name = 'remaining.product'
    _description = 'Remaining product'
    product = fields.Many2one('product.template', string='Product')
    location = fields.Many2one('stock.location',string='Location')

    def print_report(self):
        data={
            'model': 'remaining.product',
            'form' : self.read()[0]
        }
        return self.env.ref('fbno_stock_reports.action_report_pdf').report_action(self, data=data)
