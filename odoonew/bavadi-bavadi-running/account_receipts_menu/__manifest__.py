{
    'name': "Accounting Receipts Menu Hiding",
    'summary': """Hiding the Receipts Sub menu under Customers in Accounting""",
    'description': """
        -Hiding the Receipts Sub menu under Customers in Accounting
            """,
    'author': "Athira",
    'website': "http://www.febno.com",
    'category': 'Test',
    'version': '0.1',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'data/data.xml',
        'views/res_config_settings_account_view.xml',
        'views/account_menu.xml',

    ],

}
