from odoo import models, fields


class BankBookWizard(models.TransientModel):
    _inherit = 'account.bank.book.report'
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class CashBookWizard(models.TransientModel):
    _inherit = 'account.cash.book.report'
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class DayBookWizard(models.TransientModel):
    _inherit = 'account.day.book.report'
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class AccountAgedTrialBalance(models.TransientModel):
    _inherit = 'account.aged.trial.balance'
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid)]",
                                     default=lambda self: self.env.context['opid'])


class FinancialReport(models.TransientModel):
    _inherit = "financial.report"
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class FinancialReportExpenses(models.TransientModel):
    _inherit = "expenses.report"
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class AccountBalanceReport(models.TransientModel):
    _inherit = "account.balance.report"
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.common.account.report"
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])


class AccountPrintJournal(models.TransientModel):
    _inherit = "account.common.journal.report"
    operating_unit = fields.Many2one('operating.unit', 'Operating Unit', domain="[('user_ids', '=', uid), ('company_id', '=', company_id)]",
                                     default=lambda self: self.env.context['opid'])
