{
    'name': "Managing multiple operating units",
    'summary': """Managing multi-operating units""",
    'description': """
        - managing multi-operating units
        - checkbox in settings for showing operating unit field in journal lines 
            """,
    'author': "Rasha Rasheed",
    'category': 'Test',
    'version': '0.1',
    'depends': ['account', 'base_setup', 'operating_unit', 'account_department', 'account_operating_unit', 'base_accounting_kit',
                'sale_operating_unit', 'sale_operatingunit_required'],
    'data': [
        'data/groups.xml',
        'views/settings.xml',
        'views/templates.xml',
        'views/account_move.xml',
        'views/sale_views.xml',
    ],

    'demo': [
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'bootstrap': True,
}
