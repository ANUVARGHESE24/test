
{
    "name": "POS payment/order button",
    "summary": "",
    "version": "13.0.1.0.0",
    "category": "Uncategorized",
    "website": "",
    "author": "",
    "license": "AGPL-3",
    "installable": True,
    'depends': ['base','point_of_sale','pos_restaurant', 'pos_network_printer'],
    'data': [
        "views/templates.xml"

            ],
    'qweb': [
            'static/src/xml/custom_button.xml'
            ],

}
