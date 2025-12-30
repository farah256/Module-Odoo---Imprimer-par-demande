{
    'name': 'Print Customization',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage custom print orders with personalization',
    'description': """
        Simple module for managing customized 3D print orders.
        Features:
        - Custom order management
        - Color and size selection
        - Text personalization
        - File upload for custom designs
        - Simple workflow
    """,
    'author': 'X3D',
    'website': '',
    'depends': ['base', 'sale', 'product', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}