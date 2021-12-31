# -*- coding: utf-8 -*-
{
    'name': "Partner Ledger with Partner Filter-modified",

    'summary': """Modified Partner Ledger Report with Partner Filter""",

    'description': """
    - Partner Ledger Report with Partner Filter-modified
    """,
    'author': "Cybrosys Techno Solutions, Febno",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base_accounting_kit'],

    'data': [
        'views/report.xml',
        'wizard/account_report_general_ledger_view.xml'
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
