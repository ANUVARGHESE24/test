# -*- coding: utf-8 -*-
{
    'name': "Sales and Shipment Report",

    'summary': """Tree view for Sales and Shipment Report""",

    'description': """
     - 'Sales and Shipment Report' menu (Sales)
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale_delivery', 'account_delivery', 'new_fields1'],

    'data': [
        'views/shipment.xml',
    ],
}
