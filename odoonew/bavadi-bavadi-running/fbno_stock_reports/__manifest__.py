# -*- coding: utf-8 -*-
{
    'name': "Remaining Products",

    'summary': """reports on remaining products in a particular stock location""",

    'description': """
            - pdf reports
            - excel reports
        """,
    'author': "Haripriya A",
    'category': 'Test',
    'version': '0.1',
    'depends': ['stock'],
    'data': ['views/product.xml'
             ,'wizard/remaining_prdt.xml'
             ,'reports/remaining_product_report.xml'
             ,'reports/new_report.xml'],
    'demo': [],
}
