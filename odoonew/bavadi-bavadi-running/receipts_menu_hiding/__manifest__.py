{
    'name': "Receipts Menu Hiding in Accounting, Sale, Purchase",
    'summary': """Hiding the Receipts Sub menu""",
    'description': """
        -Hiding the Receipts Sub menu under Customers in Accounting
        -Hiding the Receipts Sub menu under Vendors in Accounting
        -Hiding the Receipts Sub menu under Customers in Sales
        -Hiding the Receipts Sub menu under Vendors in Purchase
            """,
    'author': "Athira",
    'website': "http://www.febno.com",
    'category': 'Test',
    'version': '0.1',
    'depends': ['base', 'sale', 'account', 'purchase', 'sales_customer', 'purchase_vendor'],
    'data': [
        'data/data.xml',
        'views/res_config_settings_account_view.xml',
        'views/account_menu.xml',
        'views/sale_menu.xml',
        'views/purchase_menu.xml',

    ],

}
