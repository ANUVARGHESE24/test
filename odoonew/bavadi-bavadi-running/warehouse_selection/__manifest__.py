{
    'name': "Warehouse Selection",
    'summary': """febno Custom""",
    'description': """
        Warehouse selection in Purchase and Sales module
            """,
    'author': "Athira",
    'website': "http://www.febno.com",
    'category': 'Test',
    'version': '0.1',
    'depends': ['base', 'stock', 'sale', 'purchase', 'sale_stock'],
    'data': [
        'data/warehouse_group.xml',
        'views/res_config_settings_inventory.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',

    ],

}
