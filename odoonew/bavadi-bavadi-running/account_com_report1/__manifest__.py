# -*- coding: utf-8 -*-
{
    'name': "Commercial Invoice PDF Report",

    'summary': """Customised Report in pdf for Accounting module""",

    'description': """ 
    - pdf print for Accounting module
    """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'account', 'account_delivery', 'new_fields1'],

    'data': [
        'views/report_templates.xml',
        'reports/account_report.xml',
    ],
}
