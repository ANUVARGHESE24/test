# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Receipt',
    'version': '13.0.1.2',
    'category': 'Point of Sale',
    'summary': 'pos receipt',
    "description": """
   odoo pos receipt
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 39,
    "currency": 'EUR',
    'depends': ['base', 'point_of_sale', 'pos_branch', 'product'],
    'data': [
        'views/pos_view.xml',
        'views/company_arabic.xml',
        'wizard/pos_dayclose_report_wizard_view.xml',
        'report/pos_order_details_report.xml',
        'report/pos_dayclose_report.xml',        
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/jMg67ck2VZA',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
