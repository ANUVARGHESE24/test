# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    warehouse_selection = fields.Boolean("Default Warehouse Selection", default=False)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_selection = fields.Boolean("Default Warehouse Selection", related='company_id.warehouse_selection')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        print("sdfghjk")
        res = super(SaleOrder, self)._onchange_company_id()
        company = self.env.company.id
        if not self.warehouse_selection:
            self.warehouse_id = False
        else:
            self.warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1).id
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    warehouse_selection = fields.Boolean("Default Warehouse Selection", related='company_id.warehouse_selection')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        res = super(PurchaseOrder, self)._onchange_company_id()
        p_type = self.picking_type_id
        if not self.warehouse_selection:
            self.picking_type_id = False
        else:
            if not (p_type and p_type.code == 'incoming' and (
                    p_type.warehouse_id.company_id == self.company_id or not p_type.warehouse_id)):
                self.picking_type_id = self._get_picking_type(self.company_id.id)
        return res
