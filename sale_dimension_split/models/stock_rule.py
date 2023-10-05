##############################################################################
#
# Copyright (c) 2023 Binhex System Solutions
# Copyright (c) 2023 Nicolás Ramos (http://binhex.es)
#
# The licence is in the file __manifest__.py
##############################################################################


from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        res = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        sale_line_id = values.get("sale_line_id", False)
        # Record can be a sale order line or a stock move depending of pull
        # and push rules
        if sale_line_id:
            record = self.env["sale.order.line"].browse(sale_line_id)
        else:
            record = values.get("move_dest_ids", self.env["stock.move"].browse())[:1]
        if record:
            res.update(
                {
                    "name": record.name,
                    "product_pieces_length": record.product_pieces_length or 0.0,
                    "product_pieces_height": record.product_pieces_height or 0.0,
                    "product_pieces_width": record.product_pieces_width or 0.0,
                    "product_number_of_pieces": record.product_number_of_pieces or 0.0,
                }
            )
        return res