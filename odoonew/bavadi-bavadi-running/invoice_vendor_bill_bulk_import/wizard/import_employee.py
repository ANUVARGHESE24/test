# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import xlrd
import babel
import logging
import tempfile
import binascii
from io import StringIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportJournal(models.TransientModel):
    _name = 'import.invoice'
    _description = 'Import customer invoices'

    file_type = fields.Selection([('CSV', 'CSV File'), ('XLS', 'XLS File')], string='File Type', default='XLS')
    invoice_type = fields.Selection(
        [('customer', 'Customer Invoice'), ('credit', 'Credit Note'), ('vendor', 'Vendor Bill'), ('refund', 'Refund')],
        string='Invoice Type')
    file = fields.Binary(string="Upload File")

    def import_invoice(self):
        if not self.file:
            raise ValidationError(_("Please Upload File to Import Journal !"))

        if self.file_type == 'CSV':
            raise ValidationError(_("Currently CSV file format is not working Please Upload Excel Sheets"))
            line = keys = ['date', 'code', 'account_id', 'partner', 'debit', 'credit']
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))
            moves_records = []
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                moves_records.append(values)
            if moves_records:
                res = self.create_employee(moves_records[1:])

        else:
            try:
                file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                file.write(binascii.a2b_base64(self.file))
                file.seek(0)
                moves_records = []
                workbook = xlrd.open_workbook(file.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))

            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))

                    values = {}
                    try:
                        values.update({
                            'operating_unit': line[0],
                            'department': line[1],
                            'invoice_date': line[2],
                            'partner_id': line[3],
                            'ref': line[4],
                            "lines": [
                                {
                                    'code': line[5],
                                    'label': line[6],
                                    'quantity': line[7],
                                    'price': line[8],
                                    'tax': line[9],
                                },
                                {
                                    'code': line[10],
                                    'label': line[11],
                                    'quantity': line[12],
                                    'price': line[13],
                                    'tax': line[14],
                                },
                                {
                                    'code': line[15],
                                    'label': line[16],
                                    'quantity': line[17],
                                    'price': line[18],
                                    'tax': line[19],
                                }
                            ]

                        })
                    except IndexError:
                        raise UserError(
                            "Excel Sheet Should have Only twenty (20) Columns..['operating_unit','department',"
                            "'invoice_date','partner_id','ref','code','label','quantity','price',,'tax','code','label','quantity','price',,'tax','code','label','quantity','price',,'tax'] ")
                    moves_records.append(values)
            logging.info("pppppppppppppppppppppppppppppppppppp values %s" % values)
            res = self.create_employee(moves_records)

    def create_employee(self, moves_records):
        invoice = self.env['account.move']
        invoice_lines = self.env['account.move.line']
        logging.info("create_employee %s" % moves_records)

        for values in moves_records:
            lines = []
            for dict in values.get("lines"):
                if dict.get('price') != '':
                    if dict.get('code') == '':
                        raise Warning(_('Account code Field can not be Empty !'))
                    account_id = self.get_account(dict.get('code'))
                    tax_ids = self.get_tax_ids(dict.get('tax'))

                    move_lines = {
                        "name": dict.get('label'),
                        'account_id': account_id.id,
                        'price_unit': float(dict.get('price')),
                        'quantity': float(dict.get('quantity')),
                        'tax_ids': [(6, 0, tax_ids)],
                        'tax_exigible': True if self.invoice_type in ('customer', 'credit') else False,
                    }
                    lines.append(move_lines)
                    logging.info("PKPKPKPKPK %s" % move_lines['price_unit'])
            date = self.get_date(values.get('invoice_date'))
            partner_id = self.get_partner(values.get('partner_id'))
            department = self.get_department_id(values.get('department'))
            operating_unit = self.get_operating_unit(values.get('operating_unit'))
            logging.info("values %s %s %s %s" % (account_id.id, department, operating_unit, tax_ids))
            vals = {
                'type': "out_invoice" if self.invoice_type == 'customer' else "in_invoice" if self.invoice_type == 'vendor' else "out_refund" if self.invoice_type == 'credit' else "in_refund",
                'ref': values.get('ref'),
                'invoice_date': date,
                "journal_id": 1 if self.invoice_type in ('customer', 'credit') else 2,
                'partner_id': partner_id.id if partner_id else False,
                'state': 'draft',
                'department_id': department.id if department else False,
                'operating_unit_id': operating_unit.id if operating_unit else False,
                'invoice_line_ids': lines,

            }
            logging.info("values %s" % vals)
            res = invoice.sudo().create(vals)

    def get_tax_ids(self, name):
        taxes = self.env['account.tax'].search([('name', '=', name)])
        tax_ids = []
        for tax in taxes:
            tax_ids.append(tax.id)
        return tax_ids

    def get_department_id(self, name):
        name = int(float(name)) if name else name
        department = self.env['hr.department'].search([('code', '=', str(name))], limit=1)
        if department:
            return department
        else:
            return False

    def get_operating_unit(self, name):
        name = int(float(name)) if name else name
        branch = self.env['operating.unit'].search([('code', '=', name)], limit=1)
        if branch:
            return branch
        else:
            return False

    def get_account(self, name):
        name = int(float(name)) if name else name
        account = self.env['account.account'].search([('code', '=', name)], limit=1)
        if account:
            return account
        else:
            raise UserError(_('"%s" Account is not found in system !') % name)

    def get_partner(self, name):
        partner = self.env['res.partner'].search([('name', '=', name)], limit=1)
        if partner:
            return partner
        else:
            return False

    def get_journal(self, name):
        journal = self.env['account.journal'].search([('name', '=', name)], limit=1)
        if journal:
            return journal
        else:
            journal = self.env['account.journal'].search(limit=1)
            return journal

    def get_date(self, account_date):
        logging.info('ppppppp*********************%s' % account_date)
        try:
            account_date = datetime.strptime(account_date, '%Y-%m-%d')
            return account_date
        except Exception:
            raise ValidationError(_('Wrong Date Format !  Should be in format YYYY-MM-DD'' and in Text format '))

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
