# -*- coding: utf-8 -*-
{
    'name': "POS back button access",

    'summary': """
        POS back button access""",

    'description': """
        POS back button access
    """,

    'author': "ALI",
    'website': "",


    'category': 'POS',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
    ],

}
