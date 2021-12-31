from odoo import api, fields, models, _


class pos_config(models.Model):
    _inherit = 'pos.config'

    telephone_no = fields.Char("Telephone No")
    address = fields.Text('Address')

class res_branch_inherit(models.Model):
    _inherit = 'res.branch'
    _rec_name = 'arabic_name'

    arabic_name = fields.Char(string='Arabic Name')


    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = rec.name  + ' ' + rec.address + ' ' + rec.phone
    #         result.append((rec.id, name ))
    #     return result



