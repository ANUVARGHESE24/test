from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = "stock.move"

    feb_cost_stck = fields.Float(string="Cost")
    feb_total_stck = fields.Float(string="Total")

    @api.onchange("product_id", 'product_uom_qty')
    def _custom_calculations(self):
        self.feb_cost_stck = self.product_id.standard_price
        self.feb_total_stck = self.feb_cost_stck * self.product_uom_qty

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    feb_cost = fields.Float(string="Cost")
    feb_total = fields.Float(string="Total")

    @api.onchange("product_id", 'qty_done')
    def _custom_calculations(self):
        self.feb_cost = self.product_id.standard_price
        self.feb_total = self.feb_cost * self.qty_done



