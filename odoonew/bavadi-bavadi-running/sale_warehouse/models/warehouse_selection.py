from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse",
                                   domain="[('operating_unit_id', '=', operating_unit_id)]")

