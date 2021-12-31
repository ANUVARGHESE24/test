# -*- coding: utf-8 -*-
{
    'name': "Odoo Debranding",

    'summary': """Odoo debranding""",

    'description': """
    - Replacing 'Powered by Odoo' with 'Powered by Febno' in login page
    - Modified User menu
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'web'],

    'data': [
        'views/login.xml',
    ],
    'qweb': [
        "static/src/xml/user_menu.xml",
    ],
}
