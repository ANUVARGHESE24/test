# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WarehouseSelection(models.TransientModel):
    _inherit = "res.config.settings"

    group_warehouse_selection = fields.Boolean("Warehouse Selection-Activation",
                                               implied_group="warehouse_selection.group_warehouse_selection")

    warehouse_selection = fields.Boolean("Default Warehouse Selection")

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('warehouse_selection.warehouse_selection', self.warehouse_selection)

        super(WarehouseSelection, self).set_values()

    @api.model
    def get_values(self):
        res = super(WarehouseSelection, self).get_values()

        res['warehouse_selection'] = self.env['ir.config_parameter'].sudo().get_param('warehouse_selection.warehouse_selection', default=0)
        return res

    @api.onchange('warehouse_selection')
    def _on_change_warehouse_selection(self):
        company_id = self.env.company
        if self.warehouse_selection:
            company_id.warehouse_selection = self.warehouse_selection
        else:
            company_id.warehouse_selection = False