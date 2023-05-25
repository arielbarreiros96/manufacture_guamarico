##############################################################################
#
# Copyright (c) 2023 Binhex System Solutions
# Copyright (c) 2023 Nicolás Ramos (http://binhex.es)
#
# The licence is in the file __manifest__.py
##############################################################################


import logging
import math

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Product dimension split"

    product_pieces_length = fields.Float(_("Largo (cm)"), store=True, default=0.0)
    product_pieces_height = fields.Float(_("Alto (cm)"), store=True, default=0.0)
    product_pieces_area = fields.Float(
        # compute="_computed_product_area",
        string=_("Piece area (cm)"),
        store=True,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    product_area = fields.Float(
        # compute="_computed_product_area",
        string=_("Total area (cm)"),
        store=True,
        digits=dp.get_precision("Product Unit of Measure"),
        default=0.0,
    )
    product_number_of_pieces = fields.Float(
        # compute="_computed_product_area",
        string=_("Piezas finales del producto"),
        store=True,
        digits=dp.get_precision("Product Unit of Measure"),
        default=0.0,
    )
    # HOJA DE CORTE
    blade_width = fields.Float(
        _("Ancho de la hoja (cm)"),
        store=True,
        default=0.0,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    blade_affects_lenght = fields.Boolean(
        _("La hoja afecta al largo"), store=True, default=False
    )
    blade_affects_height = fields.Boolean(
        _("La hoja afecta al alto"), store=True, default=False
    )
    product_pieces_length_value = fields.Float(_("Largo (cm)"), store=True)
    product_pieces_height_value = fields.Float(_("Alto (cm)"), store=True)

    sale_line_bom_ids = fields.Many2many(
        "sale.order.line.bom",
        "sale_order_line_bom_rel",
        "sale_bom_line_id",
        "order_line_id",
        string="Componentes",
        copy=False,
    )

    notes = fields.Text(_("Notas"))

    @api.depends("sale_line_bom_ids")
    def _compute_total_available(self):
        for order in self:
            available = 0.0
            for line in order.sale_line_bom_ids:
                available += line.product_qty_enter
                order.update(
                    {
                        "total_available": available,
                    }
                )

    total_available = fields.Float(
        string=_("Total disponible"),
        store=True,
        compute="_compute_total_available",
        tracking=True,
        digits="Product Unit of Measure",
    )

    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
        domain="[('product_tmpl_id.product_variant_ids', '=', product_id),"
        "'|', ('product_id', '=', product_id), "
        "('product_id', '=', False)]",
    )

    @api.constrains("bom_id", "product_id")
    def _check_match_product_variant_ids(self):
        for line in self:
            if line.bom_id:
                bom_product_tmpl = line.bom_id.product_tmpl_id
                bom_product = bom_product_tmpl.product_variant_ids
            else:
                bom_product_tmpl, bom_product = None, None
            line_product = line.product_id
            if not bom_product or line_product == bom_product:
                continue
            raise ValidationError(
                _(
                    "Please select BoM that has matched product with the line `{}`"
                ).format(line_product.name)
            )

    
    def write(self, values):
        res = super(SaleOrderLine, self).write(values)
        if self.total_available == 0:
            pass
        else:
            if self.total_available <= self.product_area:
                raise UserError(
                    _(
                        "Los componentes disponibles no cubren el área total necesario para cubrir las necesidades del cliente"
                    )
                )

        return res

    @api.onchange(
        "product_pieces_length",
        "product_pieces_height",
        "product_uom_qty",
        "blade_affects_lenght",
        "blade_affects_height",
        "sale_line_bom_ids",
        "sale_line_bom_ids.product_id",
    )
    def _computed_product_area(self):
        # self.ensure_one()
        for line in self:
            # HOJAS DE CORTE
            if line.blade_affects_lenght:
                line.product_pieces_height_value = (
                    line.product_pieces_height + line.blade_width
                )
            else:
                line.product_pieces_height_value = (
                    line.product_pieces_height - line.blade_width
                )

            if line.blade_affects_height:
                line.product_pieces_length_value = (
                    line.product_pieces_length + line.blade_width
                )
            else:
                line.product_pieces_length_value = (
                    line.product_pieces_length - line.blade_width
                )

            line.product_pieces_area = (
                line.product_pieces_height * line.product_pieces_length / 10000
            )
            line.product_area = line.product_uom_qty * line.product_pieces_height / 100
            if line.product_uom_qty != 0 and line.product_pieces_length != 0:
                line.product_number_of_pieces = math.ceil(
                    line.product_uom_qty / (line.product_pieces_length / 100)
                )

    @api.onchange(
        "sale_line_bom_ids.product_id",
        "sale_line_bom_ids",
        "product_pieces_length",
        "product_pieces_height",
        "product_uom_qty",
        "blade_affects_lenght",
        "blade_affects_height",
        "product_uom_id",
    )
    def _computed_raw_product_area(self):
        for line in self.sale_line_bom_ids:
            if line.raw_product_uom_id.uom_type == "reference":
                line.raw_product_length = line.product_id.product_length
                line.raw_product_height = line.product_id.product_height
            else:
                line.raw_product_length = line.raw_product_length
                line.raw_product_height = line.raw_product_height
            try:
                na0 = math.floor(
                    line.raw_product_length / self.product_pieces_length_value + 0.001
                )
                nl0 = math.floor(
                    line.raw_product_height / self.product_pieces_height_value + 0.001
                )
                na1 = math.floor(
                    line.raw_product_length / self.product_pieces_height_value + 0.001
                )
                nl1 = math.floor(
                    line.raw_product_height / self.product_pieces_length_value + 0.001
                )
            except ZeroDivisionError:
                na0 = 0
                nl0 = 0
                na1 = 0
                nl1 = 0

            area_h = na0 * nl0
            area_v = na1 * nl1
            raw_product_usable_area_h = area_h * self.product_pieces_area
            raw_product_usable_area_v = area_v * self.product_pieces_area
            if raw_product_usable_area_h >= raw_product_usable_area_v:
                line.raw_product_usable_area = raw_product_usable_area_h
                line.raw_area_orientation = "h"
            else:
                line.raw_product_usable_area = raw_product_usable_area_v
                line.raw_area_orientation = "v"
            line.raw_product_area = (
                line.raw_product_length * line.raw_product_height / 10000
            )

            if self.product_area != 0 and line.raw_product_usable_area != 0:
                line.product_qty = (
                    math.ceil((self.product_area / line.raw_product_usable_area))
                    * line.raw_product_area
                )
