{
    'name': "Febno Invoice Standard New - Modified",
    'summary': """Febno Invoice Standard""",
    'description': """
        - 'IBAN', 'Swift' fields in company form
        - Modified Febno Invoice Standard report 
            """,
    'author': "Rasha Rasheed",
    'website': "http://www.febno.com",
    'category': 'Test',
    'version': '0.1',
    'depends': ['account', 'base', 'bank_add'],
    'data': [
        'views/res_company.xml',
        'reports/stndrd_report.xml',
    ],

    'demo': [
    ],

}