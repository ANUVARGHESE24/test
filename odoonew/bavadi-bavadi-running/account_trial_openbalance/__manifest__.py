# -*- coding: utf-8 -*-
{
    'name': "Trial Balance with open balance",

    'summary': """ Trial Balance Report with open balance""",

    'description': """
    - Trial Balance with Open balance
    """,
    'author': "Anu Varghese",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base_accounting_kit','account'],

    'data': [
        'views/openbalance.xml',
        'report/report_openbalance.xml',
        'wizard/trial_balance.xml',
    ],
    'demo': [],

}
