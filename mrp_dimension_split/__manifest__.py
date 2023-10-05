# Copyright 2023 Nicolás Ramos - (https://binhex.es)
{
    "name": "Mrp Dimension Split",
    "version": "14.0.2.0.0",
    "category": "Manufacturing/Manufacturing",
    'summary': 'Manufacturing Orders & BOMs split production orders',
    "author": "Binhex System Solutions",
    "website": "https://binhex.es",
    "license": "AGPL-3",
    'depends': ['base', 'stock', 'mrp', 'product_dimension', 'sale_mrp_bom'],
    'data': [
        'views/mrp_production_templates_view.xml',
        'views/mrp_bom_view.xml',
        'views/stock_picking_templates_view.xml',
        'views/product_template_view.xml'
    ],
    'demo': [],
    "development_status": "Mature",
    "installable": True,
}
