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
    'depends': ['base','website','maintenance','sale','account','hr','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_request_sequence.xml',
        'data/user_portal_worker.xml',
        'views/core/maintenance_equipment.xml',
        'views/core/maintenance_request_views.xml',
        'views/custom/maintenance_type_views.xml',
        'views/custom/maintenance_task_views.xml',
        'views/custom/portal_templates.xml',
    ],
}
