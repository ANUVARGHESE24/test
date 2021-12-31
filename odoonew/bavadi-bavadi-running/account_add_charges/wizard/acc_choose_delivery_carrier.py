
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ChooseDeliveryCarrier(models.TransientModel):
    _name = 'choose.delivery.carrier.account'
    _description = 'Delivery Carrier Selection Wizard in Accounting'

    move_id = fields.Many2one('account.move', required=True, ondelete="cascade")
    partner_id = fields.Many2one('res.partner', related='move_id.partner_id', required=True)
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string="Shipping Method",
        help="Choose the method to deliver your goods",
        required=True,
    )

    delivery_type = fields.Selection(related='carrier_id.delivery_type')
    delivery_price = fields.Float()
    currency_id = fields.Many2one('res.currency', related='move_id.currency_id')
    company_id = fields.Many2one('res.company', related='move_id.company_id')
    available_carrier_ids = fields.Many2many("delivery.carrier", compute='_compute_available_carrier', string="Available Carriers")
    invoicing_message = fields.Text(compute='_compute_invoicing_message')
    delivery_message = fields.Text(readonly=True)

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        self.delivery_message = False
        if self.delivery_type in ('fixed', 'base_on_rule'):
            vals = self._get_shipment_rate()
            if vals.get('error_message'):
                return {'error': vals['error_message']}
        else:
            self.delivery_price = 0



    # @api.onchange('move_id')
    # def _onchange_move_id(self):
    #     # fixed and base_on_rule delivery price will computed on each carrier change so no need to recompute here
    #     if self.carrier_id and self.move_id.delivery_set and self.delivery_type not in ('fixed', 'base_on_rule'):
    #         vals = self._get_shipment_rate()
    #         if vals.get('error_message'):
    #             warning = {
    #                 'title': '%s Error' % self.carrier_id.name,
    #                 'message': vals.get('error_message'),
    #                 'type': 'notification',
    #             }
    #             return {'warning': warning}

    @api.depends('carrier_id')
    def _compute_invoicing_message(self):
        self.ensure_one()
        if self.carrier_id.invoice_policy == 'real':
            self.invoicing_message = _('The shipping price will be set once the delivery is done.')
        else:
            self.invoicing_message = ""



    @api.depends('partner_id')
    def _compute_available_carrier(self):
        for rec in self:
            carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', rec.move_id.company_id.id)])
            rec.available_carrier_ids = carriers.available_carriers(rec.move_id.partner_shipping_id) if rec.partner_id else carriers

    def _get_shipment_rate(self):
        vals = self.carrier_id.rate_shipment(self.move_id)
        if vals.get('success'):
            self.delivery_message = vals.get('warning_message', False)
            self.delivery_price = vals['price']
            return {}
        return {'error_message': vals['error_message']}


    def update_price(self):
        vals = self._get_shipment_rate()
        if vals.get('error_message'):
            raise UserError(vals.get('error_message'))
        return {
            'name': _('Add a shipping method'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'res_id': self.id,
            'target': 'new',
        }


    def button_confirm(self):
        self.move_id.set_delivery_line(self.carrier_id, self.delivery_price)
        self.move_id.write({
            'recompute_delivery_price': False,
            'delivery_message': self.delivery_message,
        })
