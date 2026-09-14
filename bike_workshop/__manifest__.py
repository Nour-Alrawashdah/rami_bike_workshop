{
    'name': 'Bike Workshop',
    'version': '19.0.1.5',
    'category': 'Operations',
    'summary': 'Manage bikes for rental operations',
    'depends': ['base','product'],
    'data': [
       'security/bike_security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/bike_views.xml',
        'views/rental_views.xml',
        'views/repair_views.xml',
        'views/res_partner_views.xml',
    
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}