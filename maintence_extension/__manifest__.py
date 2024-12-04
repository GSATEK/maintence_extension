# -*- coding: utf-8 -*-
{
    'name': "maintence_extension",

    'summary': """""",

    'description': """
    """,

    'author': "Alberto Ruiz",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','maintenance','sale','account','hr','mail','base_portal_type','contacts','stock','web','web_pwa_oca'],

    # always loaded
    'data': [
        'data/maintenance_request_sequence.xml',
        'data/maintenance_stage_data.xml',
        'data/user_portal_worker.xml',
        'data/maintenance_type_data.xml',
        'data/mail_templates.xml',
        'security/ir.model.access.csv',
        'views/core/maintenance_equipment.xml',
        'views/core/maintenance_request_views.xml',
        'views/custom/maintenance_type_views.xml',
        'views/custom/maintenance_task_views.xml',
        'views/custom/portal_templates.xml',
        'views/custom/import_wizzard.xml',
        'views/custom/routes_views.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'maintence_extension/static/js/maintence.js',
            'maintence_extension/static/js/maintence_products.js',
            'maintence_extension/static/scss/navbar.scss',
            'https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css',
        ],
    },
}
