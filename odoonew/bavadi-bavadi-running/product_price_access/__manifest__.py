# -*- coding: utf-8 -*-
{
    'name': "Access rights for Product prices",

    'summary': """Access rights for Product prices""",

    'description': """ 
    - access right for 'Sales price' field
    - access right for 'Cost' field
    """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'product'],

    'data': [
        'data/groups.xml',
        'views/price.xml',
    ],
}
