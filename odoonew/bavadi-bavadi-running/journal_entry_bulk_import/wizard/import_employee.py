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
    _name = 'import.journal'
    _description = 'Import Journal Entry'

    file_type = fields.Selection([('CSV', 'CSV File'), ('XLS', 'XLS File')], string='File Type', default='XLS')
    file = fields.Binary(string="Upload File")

    def import_journal(self):
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
                            'date': line[0],
                            'account': line[1],
                            'department': line[2],
                            'operating_unit': line[3],
                            'label': line[4],
                            'partner_id': line[5],
                            # 'journal_id': line[6],
                            'debit': line[6],
                            'credit': line[7],
                        })
                    except IndexError:
                        raise UserError(
                            "Excel Sheet Should have Only Eight (8) Columns..['date','code','department','operating unit','label','partner','debit','credit'] ")
                    moves_records.append(values)
            logging.info("pppppppppppppppppppppppppppppppppppp values %s" % values)
            res = self.create_employee(moves_records)

    def create_employee(self, moves_records):
        employee = self.env['account.move']
        moves = self.env['account.move.line']
        # logging.info("create_employee %s" % moves_records)
        journal_id = self.get_journal('Miscellaneous Operations')

        date = self.get_date(moves_records[0].get('date'))
        vals = {
            'date': date,
            'journal_id': journal_id.id,
            'state': 'draft',
        }

        # logging.info("create_employee before create moves employee.create(vals)")

        res = employee.create(vals)
        account_move_line_list = []
        for values in moves_records:
            if values.get('account') == '':
                raise Warning(_('Account Name Field can not be Empty !'))
            account_id = self.get_account(values.get('account'))
            partner_id = self.get_partner(values.get('partner_id'))
            department = self.get_department_id(values.get('department'))
            operating_unit = self.get_operating_unit(values.get('operating_unit'))
            move_lines = {
                'name': values.get('label'),
                'account_id': account_id.id,
                'debit': values.get('debit'),
                'credit': values.get('credit'),
                'department_id': department.id if department else False,
                'operating_unit_id': operating_unit.id if operating_unit else False,
                'partner_id': partner_id.id if partner_id else False,
                'move_id': res.id,
            }

            account_moves_lines = moves.with_context(check_move_validity=False).sudo().create(move_lines)
            account_move_line_list.append(account_moves_lines.id)
            # logging.info("create_employee out for loop  account_move_line_list %s" % account_moves_lines)

        # logging.info("PKPKPKPKPK %s" % move_lines)
        # moves = moves.create(move_lines)
        # logging.info("PKPKPKPKPK(2) %s" % moves)
        record = self.env['account.move'].browse([res.id])
        record.write({'line_ids': [(6, 0, account_move_line_list)]})
        return res

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
        account = self.env['account.account'].search([('code', '=', str(name))], limit=1)
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
            birthday = datetime.strptime(account_date, '%Y-%m-%d')
            return birthday
        except Exception:
            raise ValidationError(_('Wrong Date Format ! Date Should be in format YYYY-MM-DD'' and in Text format '))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
