from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class SaleCharges(models.Model):
    _inherit = 'sale.order'

    ship_charge = fields.Monetary(string='Shipping Charges', store=True, readonly=True)
    transport_charge = fields.Monetary(string='Transportation Charges', store=True, readonly=True)


    def _remove_delivery_line(self):
        self.env['sale.order.line'].search(
            [('order_id', 'in', self.ids), ('name', '=', 'Ship Delivery Charges')]).unlink()

    def set_delivery_line(self, carrier, amount):
        self.ship_charge = amount
        self._remove_delivery_line()
        for order in self:
            order.carrier_id = carrier.id
            order._create_delivery_line(carrier, amount)
        return True

    def action_ship_delivery_wizard(self):
        view_id = self.env.ref('sale_add_charges.sale_choose_ship_delivery_view_form').id
        if self.env.context.get('carrier_recompute'):
            name = _('Update shipping cost')
            carrier = self.carrier_id
        else:
            name = _('Add a shipping method')
            carrier = (
                self.partner_shipping_id.property_delivery_carrier_id
                or self.partner_shipping_id.commercial_partner_id.property_delivery_carrier_id
            )
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.ship.delivery.sale',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_carrier_id': carrier.id,
            }
        }

    def _remove_transport_delivery_line(self):
        self.env['sale.order.line'].search(
            [('order_id', 'in', self.ids), ('name', '=', 'Transport Delivery Charges')]).unlink()

    def set_transport_delivery_line(self, carrier, amount):
        self.transport_charge = amount
        self._remove_transport_delivery_line()
        for order in self:
            order.carrier_id = carrier.id
            order._create_delivery_line(carrier, amount)
        return True

    def action_open_delivery_wizard_sale_transport(self):
        view_id = self.env.ref('sale_add_charges.sale_choose_transport_delivery_carrier_view_form').id
        if self.env.context.get('carrier_recompute'):
            name = _('Update transportation cost')
            carrier = self.carrier_id
        else:
            name = _('Add a transportation method')
            carrier = (
                    self.partner_shipping_id.property_delivery_carrier_id
                    or self.partner_shipping_id.commercial_partner_id.property_delivery_carrier_id
            )
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.transport.delivery.carrier.sale',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_carrier_id': carrier.id,
            }
        }


    def _prepare_invoice(self):
        self.ensure_one()
        # ensure a correct context for the _get_default_journal method and company-dependent fields
        self = self.with_context(default_company_id=self.company_id.id, force_company=self.company_id.id)
        journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'ship_charge': self.ship_charge,
            'transport_charge': self.transport_charge,
        }
        return invoice_vals

