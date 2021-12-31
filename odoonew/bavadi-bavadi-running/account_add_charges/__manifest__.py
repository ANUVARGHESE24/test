# -*- coding: utf-8 -*-
{
    'name': "Additional Charges fields in Accounting",

    'summary': """Additional charges fields in Accounting""",

    'description': """
     - Shipping charge field in Invoice form (Accounting)
     - Transportation charge field in Invoice form (Accounting)
     - Checkbox for the activation of those fields in Settings
     """,
    'author': "Febno",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'account', 'delivery'],

    'data': [
        'data/delivery_method.xml',
        'data/groups.xml',
        'views/checkbox.xml',
        'views/account_charges.xml',
        'wizard/acc_choose_delivery_carrier_views.xml',
        'wizard/acc_choose_transport_delivery.xml',
    ],
}
