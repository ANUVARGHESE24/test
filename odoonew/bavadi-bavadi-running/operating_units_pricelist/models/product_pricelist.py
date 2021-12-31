# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OperatingUnits(models.Model):
    _inherit = "product.pricelist"

    operating_units = fields.Many2one('operating.unit')

    has_priceunit = fields.Boolean(compute='check_priceunit')
    user_oprunits_ids = fields.Many2many('operating.unit')

    def check_priceunit(self):
        # print("fghjk")
        logged_user = self.env.user
        operating_units_ids = logged_user.operating_unit_ids.ids
        print("operating_units_ids", operating_units_ids)
        for rec in self:
            rec.user_oprunits_ids = operating_units_ids
            rec.has_priceunit = True
            print("rec.user_oprunits_ids", rec.user_oprunits_ids)

