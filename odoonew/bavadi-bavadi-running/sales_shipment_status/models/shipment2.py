from odoo import models, fields, api


class Shipment2(models.Model):
    _inherit = "account.move"

    ship_status = fields.Selection([
        ('ld', 'Loaded'),
        ('in', 'In transit'),
        ('dp', 'Dispatched'),
    ], string='Shipment Status', compute='_ship_status')

    delivery_id = fields.Many2one('stock.picking', string='Delivery No.', compute='_delivery_id')


    def _delivery_id(self):
        for move in self:
            move.delivery_id = None
            if move.invoice_origin:
                delivery = move.env['stock.picking'].search(['&', ('origin', '=', move.invoice_origin), ('state', 'in', ['done', 'ld', 'in', 'dp'])], limit=1)
                move.delivery_id = delivery


    @api.depends('delivery_id.state')
    def _ship_status(self):
        for move in self:
            if move.delivery_id.state in ['ld', 'in', 'dp']:
                move.ship_status = move.delivery_id.state
            else:
                move.ship_status = ''








class Picking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('ld', 'Loaded'),
        ('in', 'In transit'),
        ('dp', 'Dispatched'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    hide_dispatch = fields.Boolean(default=False, help='Technical field used to compute whether the dispatch should be shown.')


    def button_load(self):
        self.state = 'ld'

    def button_transit(self):
        self.state = 'in'

    def button_dispatch(self):
        self.state = 'dp'
        self.hide_dispatch = 'True'
