from odoo import fields, models, api

class PosDaycloseReport(models.AbstractModel):
    _name = 'report.pos_receipt.fbno_pos_dayclose_report_template'
    _description = "POS Dayclose Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        print("data: ", data)
        #print("Cashier ID: ", data['form']['cashier_id'][1])
        #print("Cashier Name: ", data['form']['cashier_id'][1])

        if data['form']['cashier_id']:
            dayclose_orders = self.env['pos.order'].search(
                     [('user_id', '=', data['form']['cashier_id'][0])])
        else:
            dayclose_orders = self.env['pos.order'].search(
                [('user_id', '=', 2)]) 

        print("dayclose_orders", dayclose_orders)

        return {
            'doc_model': 'pos.order',
            'cashier': data['form']['cashier_id'][1],
            'orders': dayclose_orders,
        }



