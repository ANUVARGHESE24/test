# -*- coding: utf-8 -*-
{
    'name': "PDF Report for Sales",

    'summary': """Customised Report in pdf for Sales module""",

    'description': """ 
    - pdf print for Sales module
    """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['sale_add_charges'],

    'data': [
        'views/report_templates.xml',
        'reports/report.xml',
    ],
}
