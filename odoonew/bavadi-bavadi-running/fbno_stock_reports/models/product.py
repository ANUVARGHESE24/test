# -*- coding: utf-8 -*-
from odoo import fields, models

class Product(models.Model):

    _inherit = 'stock.warehouse'
    # _name = 'remaining.product'
    # product = fields.Many2one('product.template',string='Product')