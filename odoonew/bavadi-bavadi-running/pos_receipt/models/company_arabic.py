from odoo import models, fields, api


class CompanyToArabic(models.Model):
    _inherit = 'res.company'

    company_arabic = fields.Char(string="Arabic Name")
