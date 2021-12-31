# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TransferProductDetailsXlsx(models.AbstractModel):
    _name = 'report.febno_transfer_product.report_transfer_details_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
          print("lines",data['form_data'])

          sheet = workbook.add_worksheet('Transfer Product')
          sheet.set_column(0, 7, 20)
          cell_format = workbook.add_format({'font_size': '12px'})
          bold = workbook.add_format({'bold': True,
                                'font_size': 10,
                                })
          head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 13,
                                  'border': 1, 'bg_color': '#D3D3D3'})
          txt = workbook.add_format({'border': 1, 'font_size': 10})

          txt_left = workbook.add_format({'align': 'left',
                                    'font_size': 10,
                                    })
          txt_right = workbook.add_format({'align': 'right',
                                          'font_size': 10,
                                          })

          sheet.merge_range('A2:F2', 'Transfered Product Details', head)
          sheet.write('A6', 'Date', bold)
          sheet.write('B6', 'Source', bold)
          sheet.write('C6', 'Destination', bold)
          sheet.write('D6', 'Transfered Quantity',bold)
          sheet.write('E6', 'Cost', bold)
          sheet.write('F6', 'COGS', bold)

          # if data['form_data']['product_id'][1]:
          #     sheet.write('A8', data['form_data']['product_id'][1], cell_format)

          row_num = 7
          col_num = 0

          for product in data['products']:
              print(product)
              print(product['cost'])
              row_num += 1

              sheet.write(row_num, col_num, str(product['date']), txt_left)
              sheet.write(row_num, col_num + 1, str(product['location_id']), txt_left)
              sheet.write(row_num, col_num + 2, str(product['location_dest_id']),txt_left)
              sheet.write(row_num, col_num + 3, str(product['qty_done']), txt_right)
              sheet.write(row_num, col_num + 4, '%.2f' % (product['cost']), txt_right)
              sheet.write(row_num, col_num + 5, '%.2f' % (product['cost'] * product['qty_done']), txt_right)


