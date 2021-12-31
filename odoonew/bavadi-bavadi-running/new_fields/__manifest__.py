# -*- coding: utf-8 -*-
{
    'name': "New fields",

    'summary': """New fields in Accounting and Sales""",

    'description': """
     - 'Country of Origin' field in Invoice form (Accounting)
     - 'Vessel No.' field in Invoice form (Accounting)
     - 'Container No.' field in Quotation form (Sales)
     - 'Country of Origin' field in Quotation form (Sales)
     - 'Vessel No.' field in Quotation form (Sales)
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale_delivery', 'account_delivery'],

    'data': [
        'views/account_fields.xml',
        'views/sale_fields.xml',
    ],
}
