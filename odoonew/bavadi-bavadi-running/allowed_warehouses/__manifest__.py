{
    'name': "Allowed Warehouses",
    'summary': """febno Custom""",
    'description': """
        Allowed Warehouse selection in User settings
            """,
    'author': "Athira",
    'website': "http://www.febno.com",
    'category': 'Test',
    'version': '0.1',
    'depends': ['base', 'stock', 'purchase', 'sale_stock'],
    'data': [
        'views/res_users_view.xml',
        'security/security.xml'
    ],

}
