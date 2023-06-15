##############################################################################
#
# Copyright (c) 2023 Binhex System Solutions
# Copyright (c) 2023 Nicolás Ramos (http://binhex.es)
#
# The licence is in the file __manifest__.py
##############################################################################

{
    "name": "Sale Dimension Split",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Manufacturing Orders & BOMs split production orders",
    "author": "Binhex System Solutions",
    "website": "https://binhex.es",
    "license": "AGPL-3",
    "depends": ["base", "stock", "mrp", "product_dimension", "sale"],
    "data": [
        "reports/mrp_production_templates_view.xml",
        "reports/stock_picking_templates_view.xml",
        "reports/orden_de_trabajo_templates_view.xml",
        "views/sale_order_view.xml",
        "views/product_template_view.xml",
        "security/ir.model.access.csv"
    ],
    "demo": [],
    "development_status": "Mature",
    "installable": True,
}
