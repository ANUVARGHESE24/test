# from odoo import api, fields, models, _

# class CrmTeam(models.Model):
#
#     _inherit = "crm.team"
#
#     operating_unit_id = fields.Many2one(
#         "operating.unit",
#         default=lambda self: self.env.context['opid'],
#     )
#
#     @api.model                                                       #nothing changed now
#     @api.returns('self', lambda value: value.id if value else False)
#     def _get_default_team_id(self, user_id=None, domain=None):
#         if not user_id:
#             user_id = self.env.uid
#         team_id = self.env['crm.team'].search([
#             '|', ('user_id', '=', user_id), ('member_ids', '=', user_id),
#             '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)
#         ], limit=1)
#         if not team_id and 'default_team_id' in self.env.context:
#             team_id = self.env['crm.team'].browse(self.env.context.get('default_team_id'))
#         if not team_id:
#             team_domain = domain or []
#             default_team_id = self.env['crm.team'].search(team_domain, limit=1)
#             return default_team_id or self.env['crm.team']
#         return team_id


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

    # @api.model
    # def _get_default_team(self):
    #     print("Entered here")
    #     return self.env['crm.team']._get_default_team_id()
    #
    #
    # @api.model
    # def _default_operating_unit(self):
    #     print("Entered Sales Default............", self.env.context['opid'])
    #     opid = self.env.context['opid']
    #     # team = self.env["crm.team"]._get_default_team_id()
    #     # if team.operating_unit_id:
    #     #     print("team.op: ", team.operating_unit_id)
    #     #     return team.operating_unit_id
    #     return opid


    # team_id = fields.Many2one(
    #     'crm.team', 'Sales Team',
    #     change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    # operating_unit_id = fields.Many2one(
    #     comodel_name="operating.unit",
    #     string="Operating Unit",
    #     default=_default_operating_unit,
    #     readonly=True,
    #     states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    # )
