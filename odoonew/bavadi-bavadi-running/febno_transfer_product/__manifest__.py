
{
    "name": "Transfer Product Details",
    "summary": "Transfer Product Details in inventory",
    'description': """
       - Adding new wizard Transfer Product Details in inventory   
           """,
    "version": "13.0.1.5.1",
    "license": "LGPL-3",
    'website': "http://www.febno.com",
    "author": "Anu Varghese",
    "category": "inventory managment",
    "depends": ["stock", "report_xlsx","operating_unit"],
    "data": [

        "wizard/transproduct.xml",
        "report/report_transferproduct.xml",
        "report/report.xml",

    ],
    "installable": True,
}
