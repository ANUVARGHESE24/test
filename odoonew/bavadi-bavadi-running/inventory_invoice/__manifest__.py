# -*- coding: utf-8 -*-
{
    'name': "Invoices in Inventory",

    'summary': """Invoice field in Inventory""",

    'description': """
     - invoice field in inventory module
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'stock', 'sales_shipment_status'],

    'data': [
        'views/stock_invoice.xml',
    ],
}
