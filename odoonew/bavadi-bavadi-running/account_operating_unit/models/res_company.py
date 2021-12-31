# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ResCompany(models.Model):
    _inherit = "res.company"

    inter_ou_clearing_account_id = fields.Many2one(
        comodel_name="account.account", string="Inter-operating unit clearing account",
    )
    ou_is_self_balanced = fields.Boolean(
        string="Operating Units are self-balanced",
        help="Activate if your company is "
             "required to generate a balanced"
             " balance sheet for each "
             "operating unit.",
    )

    @api.constrains("ou_is_self_balanced", "inter_ou_clearing_account_id")
    def _inter_ou_clearing_acc_required(self):
        for rec in self:
            if rec.ou_is_self_balanced and not rec.inter_ou_clearing_account_id:
                raise UserError(
                    _(
                        "Configuration error. Please provide an "
                        "Inter-operating unit clearing account."
                    )
                )


class ResPartner(models.Model):
    _inherit = "res.partner"

    # using this method we will get payable and also liquidity accounts in partner form
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Account Payable",
                                                  domain="['|',('internal_type', '=', 'payable'),('internal_type', '=', 'liquidity'),('deprecated', '=', False)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner",
                                                  required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Account Receivable",
                                                     domain="['|',('internal_type', '=', 'receivable'),('internal_type', '=', 'liquidity'),('deprecated', '=', False)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner",
                                                     required=True)
