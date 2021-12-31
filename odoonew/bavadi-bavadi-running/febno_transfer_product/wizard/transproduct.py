# -*- coding: utf-8 -*-

from odoo import fields, models


class TransferProductDetails(models.TransientModel):
    _name = 'transfer.product.details'
    _description = 'Transfer Product Details'

    date_from = fields.Datetime('Date From', requierd=True)
    date_to = fields.Datetime('Date To', requierd=True)
    # product_id = fields.Many2one('product.product', string='Product', required=True)
    # remaining_qty = fields.Float(string='Transfered no') Afzal sir
    operating_unit_ids = fields.Many2one('operating.unit', string='Branch', required=True)

    def print_report(self):
        location = self.env['stock.location'].search([('operating_unit_id', '=', self.operating_unit_ids.id)])
        # product_id = self.product_id
        domain = [('location_id', '=', location.id)]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        products = self.env['stock.move.line'].search(domain)
        products_list = []
        for product in products:
            vals = {
                'date': product.date,
                'product_id': product.product_id.name,
                'location_id': product.location_id.name,
                'location_dest_id': product.location_dest_id.name,
                'qty_done': product.qty_done,
                'cost': product.product_id.standard_price,
            }
            products_list.append(vals)

        data = {
            'form_data': self.read()[0],
            'products': products_list
        }
        return self.env.ref('febno_transfer_product.action_report_tranfer').report_action(self, data=data)

    def get_xlsx_report(self):

        location = self.env['stock.location'].search([('operating_unit_id', '=', self.operating_unit_ids.id)])
        # product_id = self.product_id
        domain = [('location_id', '=', location.id)]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        products = self.env['stock.move.line'].search(domain)
        products_list = []
        for product in products:
            vals = {
                'date': product.date,
                'product_id': product.product_id.name,
                'location_id': product.location_id.name,
                'location_dest_id': product.location_dest_id.name,
                'qty_done': product.qty_done,
                'cost': product.product_id.standard_price,
            }
            products_list.append(vals)

        data = {
            'form_data': self.read()[0],
            'products': products_list
        }
        return self.env.ref('febno_transfer_product.action_report_tranfer_xls').report_action(self, data=data)
