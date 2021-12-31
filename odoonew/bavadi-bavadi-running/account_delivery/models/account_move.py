# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="Fill this field if you plan to invoice the shipping based on picking.")
    delivery_message = fields.Char(readonly=True, copy=False)
    delivery_rating_success = fields.Boolean(copy=False)
    delivery_set = fields.Boolean(compute='_compute_delivery_state')
    recompute_delivery_price = fields.Boolean('Delivery cost should be recomputed')
    is_all_service = fields.Boolean("Service Product", compute="_compute_is_service_products")

    @api.depends('invoice_line_ids')
    def _compute_is_service_products(self):
        for so in self:
            so.is_all_service = all(line.product_id.type == 'service' for line in so.invoice_line_ids)

    def _compute_amount_total_without_delivery(self):
        self.ensure_one()
        delivery_cost = sum([l.price_total for l in self.invoice_line_ids if l.is_delivery])
        return self.amount_total - delivery_cost

    @api.depends('invoice_line_ids')
    def _compute_delivery_state(self):
        for order in self:
            order.delivery_set = any(line.is_delivery for line in order.invoice_line_ids)

    @api.onchange('invoice_line_ids', 'partner_id')
    def onchange_invoice_line_ids(self):
        delivery_line = self.invoice_line_ids.filtered('is_delivery')
        if delivery_line:
            self.recompute_delivery_price = True



    def set_delivery_line(self, carrier, amount):
        self.ship_charge = amount
        for order in self:
            order.carrier_id = carrier.id
            order._create_delivery_line(carrier, amount)
        return True


    def set_transport_delivery_line(self, carrier, amount):
        self.transport_charge = amount
        for order in self:
            order.carrier_id = carrier.id
            order._create_transport_delivery_line(carrier, amount)
        return True



    def action_open_delivery_wizard_ship(self):
        view_id = self.env.ref('account_delivery.account_choose_delivery_carrier_view_form').id
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
            'res_model': 'choose.delivery.carrier.account',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_carrier_id': carrier.id,
            }
        }

    def action_open_delivery_wizard_transport(self):
        view_id = self.env.ref('account_delivery.account_choose_transport_delivery_carrier_view_form').id
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
            'name': "Add a transportation method",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.transport.delivery.carrier.account',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_transport_carrier_id': carrier.id,
            }
        }




    def _create_delivery_line(self, carrier, price_unit):
        AccountMoveLine = self.env['account.move.line']

        if self.partner_id:
            # set delivery detail in the customer language
            carrier = carrier.with_context(lang=self.partner_id.lang)

        # Apply fiscal position
        taxes = carrier.product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes_ids = taxes.ids
        if self.partner_id and self.fiscal_position_id:
            taxes_ids = self.fiscal_position_id.map_tax(taxes, carrier.product_id, self.partner_id).ids

        # Create the invoice order line
        carrier_with_partner_lang = carrier.with_context(lang=self.partner_id.lang)
        if carrier_with_partner_lang.product_id.description_sale:
            so_description = '%s: %s' % (carrier_with_partner_lang.name,
                                        carrier_with_partner_lang.product_id.description_sale)
        else:
            so_description = carrier_with_partner_lang.name
        values = {
            'move_id': self.id,
            'name': so_description,
            'quantity': 1,
            'account_id': carrier.product_id.property_account_income_id.id or carrier.product_id.property_account_expense_id.id,
            'product_uom_id': carrier.product_id.uom_id.id,
            'product_id': carrier.product_id.id,
            'tax_ids': [(6, 0, taxes_ids)],
            'credit': price_unit,
            'debit': 0.0,
            'is_delivery': True,
            'currency_id': False,
            'exclude_from_invoice_tab': False,
        }
        account = self.env['account.account'].search(['|', ('user_type_id', '=', 'account.data_account_type_receivable'), ('name', '=', 'Accounts Receivable')])

        if carrier.invoice_policy == 'real':
            values['price_unit'] = 0
            values['name'] += _(' (Estimated Cost: %s )') % self._format_currency_amount(price_unit)
        else:
            values['price_unit'] = price_unit
        if carrier.free_over and self.currency_id.is_zero(price_unit):
            values['name'] += '\n' + 'Free Shipping'
        if self.invoice_line_ids:
            values['sequence'] = self.invoice_line_ids[-1].sequence + 1

        sol = AccountMoveLine.sudo().with_context(check_move_validity=False).create(values)


        # ...........balancing...............
        b = self.env['account.move.line'].search([('move_id', 'in', self.ids), ('name', '=', 'Ship Delivery Charges')])
        for line in self.line_ids:
            if len(b) > 1:
                if line == b[0]:
                    continue
            if line.account_id == account:
                if len(b) <= 1:
                    line.debit = line.debit + price_unit
                if len(b) > 1:
                    a = b[0].price_unit
                    b[0].sudo().with_context(check_move_validity=False).unlink()
                    line.debit = line.debit - a + b[1].price_unit
            else:
                pass
        return sol



    def _create_transport_delivery_line(self, carrier, price_unit):
        AccountMoveLine = self.env['account.move.line']

        if self.partner_id:
            # set delivery detail in the customer language
            carrier = carrier.with_context(lang=self.partner_id.lang)

        # Apply fiscal position
        taxes = carrier.product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes_ids = taxes.ids
        if self.partner_id and self.fiscal_position_id:
            taxes_ids = self.fiscal_position_id.map_tax(taxes, carrier.product_id, self.partner_id).ids

        # Create the invoice order line
        carrier_with_partner_lang = carrier.with_context(lang=self.partner_id.lang)
        if carrier_with_partner_lang.product_id.description_sale:
            so_description = '%s: %s' % (carrier_with_partner_lang.name,
                                         carrier_with_partner_lang.product_id.description_sale)
        else:
            so_description = carrier_with_partner_lang.name
        values = {
            'move_id': self.id,
            'name': so_description,
            'quantity': 1,
            'account_id': carrier.product_id.property_account_income_id.id or carrier.product_id.property_account_expense_id.id,
            'product_uom_id': carrier.product_id.uom_id.id,
            'product_id': carrier.product_id.id,
            'tax_ids': [(6, 0, taxes_ids)],
            'credit': price_unit,
            'debit': 0.0,
            'is_delivery': True,
            'currency_id': False,
            'exclude_from_invoice_tab': False,
        }
        account = self.env['account.account'].search(['|', ('user_type_id', '=', 'account.data_account_type_receivable'), ('name', '=', 'Accounts Receivable')])

        if carrier.invoice_policy == 'real':
            values['price_unit'] = 0
            values['name'] += _(' (Estimated Cost: %s )') % self._format_currency_amount(price_unit)
        else:
            values['price_unit'] = price_unit
        if carrier.free_over and self.currency_id.is_zero(price_unit):
            values['name'] += '\n' + 'Free Shipping'
        if self.invoice_line_ids:
            values['sequence'] = self.invoice_line_ids[-1].sequence + 1

        sol = AccountMoveLine.sudo().with_context(check_move_validity=False).create(values)

        # ..........balancing..............
        c = self.env['account.move.line'].search([('move_id', 'in', self.ids), ('name', '=', 'Transport Delivery Charges')])
        for line in self.line_ids:
            if len(c) > 1:
                if line == c[0]:
                    continue
            if line.account_id == account:
                if len(c) <= 1:
                    line.debit = line.debit + price_unit
                if len(c) > 1:
                    a = c[0].price_unit
                    c[0].sudo().with_context(check_move_validity=False).unlink()
                    line.debit = line.debit - a + c[1].price_unit
            else:
                pass
        return sol



    def _format_currency_amount(self, amount):
        pre = post = u''
        if self.currency_id.position == 'before':
            pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=self.currency_id.symbol or '')
        else:
            post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=self.currency_id.symbol or '')
        return u' {pre}{0}{post}'.format(amount, pre=pre, post=post)

    # @api.depends('invoice_line_ids.is_delivery', 'invoice_line_ids.is_downpayment',
    #              'invoice_line_ids.product_id.invoice_policy')
    # def _get_invoice_status(self):
    #     super()._get_invoice_status()
    #     for order in self:
    #         if order.invoice_status in ['no', 'invoiced']:
    #             continue
    #         invoice_line_idss = order.invoice_line_ids.filtered(lambda x: not x.is_delivery and not x.is_downpayment and not x.display_type)
    #         if all(line.product_id.invoice_policy == 'delivery' and line.invoice_status == 'no' for line in invoice_line_idss):
    #             order.invoice_status = 'no'




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_delivery = fields.Boolean(string="Is a Delivery", default=False)
    product_qty = fields.Float(compute='_compute_product_qty', string='Product Qty', digits='Product Unit of Measure')
    recompute_delivery_price = fields.Boolean(related='move_id.recompute_delivery_price')

    # @api.depends('product_id', 'uom', 'quantity')
    # def _compute_product_qty(self):
    #     for line in self:
    #         if not line.product_id or not line.uom or not line.quantity:
    #             line.product_qty = 0.0
    #             continue
    #         line.product_qty = line.product_uom._compute_quantity(line.quantity, line.product_id.uom_id)

    def unlink(self):
        for line in self:
            if line.is_delivery:
                line.move_id.carrier_id = False
        super(AccountMoveLine, self).unlink()
        return True

    def _is_delivery(self):
        self.ensure_one()
        return self.is_delivery


    # override to allow deletion of delivery line in a confirmed order
    def _check_line_unlink(self):
        undeletable_lines = super()._check_line_unlink()
        return undeletable_lines.filtered(lambda line: not line.is_delivery)
