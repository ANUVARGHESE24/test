from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_department_accounting = fields.Boolean("Department Accounting", implied_group="account_department.group_department_accounting")
    group_import_journal = fields.Boolean("Import Journal Entries", implied_group="account_department.group_import_journal")

