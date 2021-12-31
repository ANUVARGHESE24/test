
{
    "name": "Day Close Report",
    "summary": " Day Close Report in accounting",
    'description': """
       - Adding Day Close Report in accounting    
           """,
    "version": "13.0.1.5.1",
    "license": "LGPL-3",
    'website': "http://www.febno.com",
    "author": "Anu Varghese",
    "category": "inventory managment",
    "depends": ["account", "report_xlsx"],
    "data": [

        "wizard/dayclose_report_wizard_view.xml",
        "report/dayclose_report.xml",


    ],
    "installable": True,
}
