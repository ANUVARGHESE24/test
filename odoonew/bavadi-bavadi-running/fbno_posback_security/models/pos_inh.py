# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosConfigInh(models.Model):
    _inherit = 'pos.config'

    back_button = fields.Boolean(string="POS Back button", default=False)
    back_button_password = fields.Char(string=u"Password")

    @api.constrains('back_button_password')
    def check_back_button_password(self):
        if self.back_button is True:
            for item in str(self.back_button_password):
                try:
                    int(item)
                except Exception as e:
                    raise ValidationError(_("The Back button password should be a number"))
