from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = "stock.picking"

    invoices = fields.Many2one('account.move', string='Invoices')


    @api.onchange('invoices')
    def _onchange_invoices_auto_complete(self):

        self.partner_id = self.invoices.partner_id
        self.origin = self.invoices.invoice_origin
        self.invoice_delivery_id = self.invoices.delivery_id
       
        new_lines = self.env['stock.move']
        for inv in self.invoices.invoice_line_ids:
            values = {
                'name': _('New Move:') + inv.product_id.display_name,
                'product_id': inv.product_id.id,
                'product_uom_qty': inv.quantity,
                'product_uom': inv.product_uom_id.id,
                'description_picking': inv.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_id': self.id,
                'picking_type_id': self.picking_type_id.id,
                'company_id': inv.company_id.id,
            }
            lines = new_lines.create(values)

