# -*- coding: utf-8 -*-
{
    'name': "itriplee",

    'summary': """
        Modulos completos desarrollados para ITRIPLEE""",
    'description': """
        Modulo de Cotizaciones para las marcas Vogar y Salicru asi como baterias, servicios, transformadores, plantas de emergencia y toda la linea de Productos de Itriplee. 

        Modulo de Marketing

        Modulo de Servicios y seguimiento al cliente con reportes asi como control de calidad

        Modulos de seguimiento de Garantias y Polizas de Mantenimiento
    """,

    'author': "Sitecnet",
    'website': "http://www.sitecnet.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Produccion',
    'version': '1.5',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts', 'base_setup', 'web_google_maps','decimal_precision'],

    # always loaded
    'data': [
        'security/itriplee_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml', #Es la vista del catalogo
        'views/templates.xml',
        'views/cotizaciones.xml',
        'views/servicios.xml',
        'views/polizas.xml',
        'views/garantias.xml',
        'views/equipos.xml',      
        'views/heredado.xml',        
        'report/cotizaciones_template.xml',
        'report/cotizaciones_report.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
