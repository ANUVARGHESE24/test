from odoo import api, fields, models


class SaleCharges(models.Model):
    _inherit = 'sale.order'

    ship_charge = fields.Monetary(string='Shipping Charges', store=True)
    transport_charge = fields.Monetary(string='Transportation Charges', store=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_new', tracking=4)



    @api.depends('order_line.price_total', 'ship_charge', 'transport_charge')
    def _amount_all_new(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax + self.ship_charge + self.transport_charge,
            })