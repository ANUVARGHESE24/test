from odoo import fields, models, api


class PosDaycloseReportWizard(models.TransientModel):
    _name = "pos.dayclose.report.wizard"
    _description = "POS DayClose Report"

    cashier_id = fields.Many2one("res.users", string="Cashier")

    def print_pos_dayclose_report(self):
        #print("self.read()[0]: ", self.read()[0])
        data = {
            'model': 'pos.dayclose.report.wizard',
            'form': self.read()[0],
        }
        
        # The following code will be used when abstract model in report folder is not created  
        # print("data: ", data)
        # print("Cashier ID: ", data['form']['cashier_id'][0])
        # print("Cashier Name: ", data['form']['cashier_id'][1])
        # dayclose_orders = self.env['pos.order'].search(
        #     [('user_id', '=', data['form']['cashier_id'][0])])
        # print("dayclose_orders", dayclose_orders)
        # dayclose_orders_list = []
        # for order in dayclose_orders:
        #     values = {
        #         'name': order.name,
        #         'pos_reference': order.pos_reference,
        #         'amount_total': order.amount_total
        #     }
        #     dayclose_orders_list.append(values)
        # data['orders'] = dayclose_orders_list

        return self.env.ref(
            'pos_receipt.fbno_pos_dayclose_report').report_action(self, data=data)

