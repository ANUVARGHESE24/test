from odoo import api, models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        session_new = super(Http, self).session_info()
        user_context = request.session.get_context() if request.session.uid else {}


        session_new.update({
            "user_op_units": {'current_op_unit': (user.default_operating_unit_id.id, user.default_operating_unit_id.name),
                              'allowed_op_units': [(op.id, op.name) for op in user.operating_unit_ids]},
            "display_switch_op_unit_menu": len(user.operating_unit_ids) > 1,
        })
        return session_new
