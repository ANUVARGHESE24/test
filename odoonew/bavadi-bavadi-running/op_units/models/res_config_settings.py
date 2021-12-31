from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_op_unit(self):
        user = self.env['res.users'].browse(self.env.uid)
        opid = self.env.context.get('opid') 
        if self.env.context.get('opid'):
            current_op_unit = self.env['operating.unit'].browse(opid)
        else:
            current_op_unit = user.default_operating_unit_id
        if current_op_unit.company_id != self.env.company:
            raise UserError(_(f"The Operating Unit '{current_op_unit.name}' doesn't come under the current Company '{self.env.company.name}'. \nPlease select another Operating Unit."))
        op_unit = current_op_unit     
        return op_unit


    group_op_unit_in_journal_lines = fields.Boolean("Operating Unit field in Journal lines", implied_group="op_units.group_op_unit_in_journal_lines")
    op_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True, default=_default_op_unit, store=True)
    op_unit_name = fields.Char(compute="_compute_op_unit_informations")
    op_unit_count = fields.Integer('Number of Operating Units', compute="_compute_op_unit_count")
    op_unit_informations = fields.Text(compute="_compute_op_unit_informations")


    def open_op_unit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Operating Unit',
            'view_mode': 'form',
            'res_model': 'operating.unit',
            'res_id': self.op_unit_id.id,
            'target': 'current',
            'context': {
                'form_view_initial_mode': 'edit',
            },
        }

    @api.depends('op_unit_id')
    def _compute_op_unit_count(self):
        user = self.env['res.users'].browse(self.env.uid)
        op_unit_count = len(user.operating_unit_ids)
        # op_unit_count = self.env['res.users'].sudo().search_count([('operating_unit_ids')])
        for record in self:
            record.op_unit_count = op_unit_count

    @api.depends('op_unit_id')
    def _compute_op_unit_informations(self):
        name = '%s\n' % self.op_unit_id.name
        informations = '%s\n' % self.op_unit_id.code
        informations += '%s\n' % self.op_unit_id.partner_id.name
        informations += '%s\n' % self.op_unit_id.company_id.name

        for record in self:
            record.op_unit_informations = informations
            record.op_unit_name = name
