# -*- coding: utf-8 -*-
{
    'name': "PDF Report",

    'summary': """Customised Report in pdf""",

    'description': """ 
    - pdf print for Sales module

    """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale'],

    'data': [
        'views/report_templates.xml',
        'reports/report.xml',
        # 'reports/account_report.xml',
    ],
}
