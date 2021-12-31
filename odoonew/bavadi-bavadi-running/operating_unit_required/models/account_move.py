from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _default_operating_unit_id(self):
        if (
                self._context.get("default_type", False)
                and self._context.get("default_type") != "entry"
        ):
            return self.env["res.users"].operating_unit_default_get()
        return False

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        required="True",
        default=_default_operating_unit_id,
        domain="[('user_ids', '=', uid)]",
        help="This operating unit will be defaulted in the move lines.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
