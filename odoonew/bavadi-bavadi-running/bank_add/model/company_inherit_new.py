from odoo import models, fields


class InheritCompany(models.Model):
    _inherit = "res.company"

    pancardnumber = fields.Char(string="Pan No")
    bank_name = fields.Char(string="Bank name")
    accno = fields.Char(string="Account Number")
    ifcode = fields.Char(string="IFSC Code")
    brname = fields.Char(string="Branch")
    payeeid = fields.Char(string="Payee")
    bank_name_2 = fields.Char(string="Bank name 2")
    accnom = fields.Char(string="Account Number")
    ifscode = fields.Char(string="IFSC Code")
    branname = fields.Char(string="Branch")
    payeeids = fields.Char(string="Payee")









