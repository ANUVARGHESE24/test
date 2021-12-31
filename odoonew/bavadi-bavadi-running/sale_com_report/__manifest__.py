# -*- coding: utf-8 -*-
{
    'name': "Commercial Invoice PDF Report for Sales",

    'summary': """Customised Report in pdf for Sales module""",

    'description': """ 
    - pdf print for Sales module
    """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale', 'sale_delivery', 'new_fields'],

    'data': [
        'views/report_templates.xml',
        'reports/sale_report.xml',
    ],
}
