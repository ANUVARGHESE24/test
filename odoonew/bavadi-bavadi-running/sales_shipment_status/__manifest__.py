# -*- coding: utf-8 -*-
{
    'name': "Shipment Status",

    'summary': """Shipment Status in 'Sales and Shipment Report'""",

    'description': """
     - shipment status column in 'Sales and Shipment Report' view
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sales_shipment_view'],

    'data': [
        'views/account_move.xml',
        'views/shipment2.xml',
    ],
}
