from odoo import fields, models, api

class DaycloseReportWizard(models.TransientModel):
    _name = "dayclose.report.wizard"
    _description = "DayClose Report"

    date_from = fields.Date('Date From', requierd=True)
    date_to = fields.Date('Date To', requierd=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True)

    def print_dayclose_report(self):

        operating_units = self.env['account.payment'].search([('payment_type', '=', 'inbound'),('operating_unit_id', '=',
                                self.operating_unit_id.id),('payment_date', '>=', self.date_from),('payment_date', '<=', self.date_to)
                                                              ])

        unit_list = []

        for unit in operating_units:
            vals = {
                   'name': unit.name,
                   'operating_unit_id': unit.operating_unit_id.name,
                   'journal_id': unit.journal_id.name,
                   'amount': unit.amount,
            }
            unit_list.append(vals)

        data = {
            'form_data': self.read()[0],
            'units': unit_list
        }
        return self.env.ref('febno_dayclose_report.dayclose_report').report_action(self, data=data)




