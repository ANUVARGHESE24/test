{
    'name': "Odoo Debranding2",

    'summary': """Odoo debranding""",

    'description': """
    - Replacing 'Powered by Odoo' with 'Powered by Febno' in Report previews
    - Replacing 'Powered by Odoo' with 'Powered by Febno' in web templates
     """,
    'author': "Rasha Rasheed",
    'website': "",
    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'web', 'account', 'portal'],

    'data': [
        'views/web_templates.xml',
        'views/preview.xml',
    ],
}
