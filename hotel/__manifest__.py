# -*- coding: utf-8 -*-
{
    'name': 'hotel',

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': 'Lolo',
     'website': "https://github.com/BAGATHE",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Industry Specific',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'icon': '/hotel/static/src/img/hotel.svg',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
}

