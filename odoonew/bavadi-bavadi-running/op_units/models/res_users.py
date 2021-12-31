from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _default_operating_unit(self):
        a = []
        current_comp = self.env.company
        ops = self.env['operating.unit'].search([('company_id', '=', current_comp.id)])
        for i in ops:
            a.append(i)
        return a[0]


    default_operating_unit_id = fields.Many2one(
        "operating.unit",
        "Default Operating Unit",
        default=lambda self: self._default_operating_unit(),
        required=True,
        # domain=[('company_id', '=', lambda self: self.env.company.id)]
    )

    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "operating_unit_users_rel",
        "user_id",
        string="Operating Units",
        # default=lambda self: self._default_operating_units(),
    )


