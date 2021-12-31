# -*- coding: utf-8 -*-
{
    'name': "Department Accounting",

    'summary': """Department Accounting""",

    'description': """
     - Activation of 'Import journal entries' menu in 'account' module
     - Department Accounting
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'account', 'journal_entry_bulk_import', 'base_accounting_kit'],

    'data': [
        'data/groups.xml',
        'views/department.xml',
        'wizards/wizards.xml',
    ],
}
