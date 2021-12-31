# -*- coding: utf-8 -*-
{
    'name': "Additional Charges fields",

    'summary': """Additional charges fields in Sales and Accounting""",

    'description': """
     - Shipping charge field in Quotation form (Sales)
     - Transportation charge field in Quotation form (Sales)
     - Checkbox for the activation of those fields in Settings
     - Shipping charge field in Invoice form (Accounting)
     - Transportation charge field in Invoice form (Accounting)
     - Checkbox for the activation of those fields in Settings
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale', 'account'],

    'data': [
        'data/groups.xml',
        'views/checkbox.xml',
        'views/sale_charges.xml',
        'views/account_charges.xml',
    ],
}
