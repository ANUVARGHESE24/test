# -*- coding: utf-8 -*-
{
    'name': "Delivery Charges fields in Sales",

    'summary': """Delivery charges fields in Sales module""",

    'description': """
     - Shipping charge field in Quotation form (Sales)
     - Transportation charge field in Quotation form (Sales)
     - Checkbox for the activation of those fields in Settings
     """,
    'author': "Febno",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale', 'delivery', 'account_delivery'],

    'data': [
        'data/groups.xml',
        'views/checkbox.xml',
        'views/sale_charges.xml',
        'wizard/sale_choose_transport_delivery.xml',
        'wizard/sale_choose_ship_delivery.xml',
    ],
}
