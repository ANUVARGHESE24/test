

from odoo import models, fields , api

class delivery_mode(models.Model):
	_name = 'pos.deliverymode'
	_order = 'sequence'
	_description = "POS order delivery mode"
	
	name = fields.Char(required=True)
	sequence = fields.Float(required=True , string='Sequence',default=1)


class pos_order_extends_for_delivery_mode(models.Model):
	_inherit = "pos.order"
	_description = "Point of Sale Extension"

	delivery_mode_id = fields.Many2one('pos.deliverymode', string='Delivery Mode')

	@api.model
	def _order_fields(self, ui_order):
		res = super(pos_order_extends_for_delivery_mode, self)._order_fields(ui_order)
		res['delivery_mode_id'] = ui_order.get('delivery_mode_id' == 1)
		return res 
