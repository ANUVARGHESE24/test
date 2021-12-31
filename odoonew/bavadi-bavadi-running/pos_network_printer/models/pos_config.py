# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    ticket_print_mode = fields.Selection([('web', 'Web'), ('network', 'Network')], string='Ticket print mode', default='web', required=True)
    bill_print_mode = fields.Selection([('web', 'Web'), ('network', 'Network')], string='Bill print mode', default='web', required=True)
    network_printer_ids = fields.Many2many('network.printer', string='Network printers')
    printing_mode = fields.Selection([('offline', 'Offline'), ('online', 'Online')], string='Printing mode', default='offline', required=True)
    kot_receipt_printing = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], string='KOT Receipt Printing', default='manual')

