# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Import invoice_& vendor bills bulk import Excel",
    'version': "13.0.0.0",
    'category': "Accounts",
    # 'summary': "Apps helps to import invoices and vendor bills from excel import multiple invoices,
    # import from excel",
    # 'description':	"""
    # 				import employee  import multiple employee  import bulk employee
    # 				import employee from excel  import employee from xls
    # 				import employee from csv  import multiple employee from xls and csv
    # 				""",
    'author': "Febno technologies",
    "website": "https://www.febnotechnologies.in",
    "price": 00,
    "currency": 'EUR',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_employee_view.xml',
        'views/import_bills_menu.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    # "live_test_url": 'https://youtu.be/RTNuwTx2Y1Q',
    # "images": ['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
