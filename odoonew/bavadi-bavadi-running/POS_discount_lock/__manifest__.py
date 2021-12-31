# -*- coding: utf-8 -*-

{
    'name': "POS DISCOUNT LOCK",
    'summary': """
        Lock change discount or price in Point Of Sale""",
    'description': """
            Lock change discount or price in Point Of Sale""",
    'author': "AKBAR ALI A",
    'website': "",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'images': ['static/description/lock.jpg'],
    'version': '13',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/pos_view.xml',
    ],

}
