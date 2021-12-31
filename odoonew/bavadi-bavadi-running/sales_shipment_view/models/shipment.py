from odoo import models, fields, api

class Shipment(models.Model):
    _inherit = "account.move"

    total_qty = fields.Float(string="Total Quantity", compute='_total_qty', store=True)
    untaxed = fields.Float(string="Total Price", compute='_total_qty', store=True)
    dest = fields.Char(string="Destination", compute='_destination')

    @api.depends('invoice_line_ids.quantity')
    def _total_qty(self):
        for move in self:
            total_qty = 0
            total_price = 0
            for line in move.invoice_line_ids:
                if line.name != 'Ship Delivery Charges':
                    if line.name != 'Transport Delivery Charges':
                        total_qty += line.quantity
                        total_price += line.price_total
                move.total_qty = total_qty
                move.untaxed = total_price


    @api.depends('partner_id')
    def _destination(self):
        for move in self:
            if move.partner_id:
                partner = move.partner_id
                dest = partner.city
                dest1 = partner.country_id.name
                move.dest = str(dest) + "," + str(dest1)
            else:
                move.dest = None
