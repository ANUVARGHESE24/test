{
    'name': "Required Operating Unit Field in Sales",
    'summary': """Required Operating Unit Field""",
    'description': """
       - Changing the postion of Operating Unit Field
       - Making Operating Unit Field Required
            """,
    'author': "Athira",
    'website': "http://www.febno.com",
    'category': 'Test',
    'version': '0.1',
    'depends': ['base', 'stock', 'sale', 'purchase', 'sale_stock'],
    'data': [
        'views/sale_order_view.xml',
    ],

}
