{
    'name': 'Bike Workshop',

    'version': '19.0.1.5',

    'category': 'Operations',

    'summary': 'Manage bikes for rental operations',

    'depends': ['base', 'product', 'portal'],

    'data': [
        'security/bike_security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/bike_views.xml',
        'views/rental_views.xml',
        'views/repair_views.xml',
        'views/res_partner_views.xml',
        'views/dashboard_views.xml',
        'report/rental_report.xml',
        'report/rental_report_templates.xml',
        'views/portal_templates.xml',
        'views/rental_analysis_views.xml',
        'data/company_logo.xml'
    ],

    'assets': {
        'web.assets_backend': [
            'bike_workshop/static/src/css/branding.css',
        ],
    },

    'installable': True,

    'application': True,

    'license': 'LGPL-3',
}