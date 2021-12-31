# -*- coding: utf-8 -*-
{
    'name': "Module access",

    'summary': """
        Visibillity of modules""",

    'description': """
        Set Visibillity of modules
    """,

    'author': "Akbar",
    'website': "",


    'category': 'Security',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'hr', 'stock', 'contacts', 'purchase', 'hr_holidays', 'calendar', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',

    ],

}
