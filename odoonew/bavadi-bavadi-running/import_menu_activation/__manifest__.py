# -*- coding: utf-8 -*-
{
    'name': "Import-Menu Activations",

    'summary': """Import menu activations in Purchase & Sales modules""",

    'description': """ 
    - Checkbox for the activation of 'Import Vendor bills' in Purchase module
    - Checkbox for the activation of 'Import Invoice bills' in Sales module
    """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['purchase_vendor', 'sales_customer'],

    'data': [
        'data/groups.xml',
        'views/import_check_view.xml',
    ],
}
