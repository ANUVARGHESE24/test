{
    'name': "POS Delivery mode Selection / POS Delivery Mode",
    'version' : '13.0.1',
    'summary': 'Delivery Mode will determine the mode of delivery such as dine in take away etc',
    'category': 'Point of Sale',
    'description': """ Pos outlet may have multiple delivery system such as dine in, take away,delivery etc.
				Based on the delivery mode system will dynamically adjust the input field requierd at the front end such as Customer name Contact no etc """,
    'price': 10,
    'currency': 'EUR',
    "author" : "MAISOLUTIONSLLC",
    'sequence': 1,
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    'license': 'OPL-1',
    'depends' : ['base','web','product','point_of_sale'],
    'data': [
		'security/ir.model.access.csv',
		'demo/delivery_mode_demo.xml',
		'views/templates.xml',
		'views/delivery_mode_view.xml',
    ],
    'images': [],
	'qweb' : [
		'static/src/xml/delivery_mode.xml',
		'static/src/xml/toppings.xml',
	],
    'images': ['static/description/main_screenshot.png'],
    "live_test_url" : "https://youtu.be/kORCCUJIdnE ",
    'installable': True,
    'application': True,
    'auto_install': False,
}

