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


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        if self.sale_line_id and self.sale_line_id.bom_id:
            values["bom_id"] = self.sale_line_id.bom_id
        return values
