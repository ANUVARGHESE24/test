# -*- coding: utf-8 -*-
{
    'name': "Account Payments Amount Due",

    'summary': """Account Payments Amount Due""",

    'description': """
     - Listing Invoice Numbers of a selected customer in Payments form
     - Displaying Due Amount Of selected invoice
     """,
    'author': "Athira",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale', 'account'],

    'data': [
        'views/account_payment_form.xml',
    ],
}
