from odoo import models


class FinancialReport(models.TransientModel):
    _inherit = "financial.report"


class FinancialReportExpenses(models.TransientModel):
    _inherit = "expenses.report"

class AccountBalanceReport(models.TransientModel):
    _inherit = "account.balance.report"
