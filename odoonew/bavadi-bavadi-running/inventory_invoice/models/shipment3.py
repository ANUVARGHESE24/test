from odoo import models, fields


class Shipment2(models.Model):
    _inherit = "account.move"

    delivery_id = fields.Many2one('stock.picking', string='Delivery No.', compute='_delivery_id')

    def _delivery_id(self):
        for move in self:
            move.delivery_id = None
            if move.invoice_origin:
                delivery = move.env['stock.picking'].search([('origin', '=', move.invoice_origin), ('state', 'in', ['done', 'ld', 'in', 'dp'])], limit=1)
                move.delivery_id = delivery
            if not move.invoice_origin:
                delivery = move.env['stock.picking'].search(['&', ('invoices', '=', move.id), ('origin', '=', move.invoice_origin), ('state', 'in', ['done', 'ld', 'in', 'dp'])], limit=1)
                move.delivery_id = delivery
