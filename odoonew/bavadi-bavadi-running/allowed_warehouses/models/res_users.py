# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AllowedWh(models.Model):
    _inherit = "res.users"

    default_picking_type_ids = fields.Many2many('stock.warehouse', string='Default Warehouses')
