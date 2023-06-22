import io
from base64 import urlsafe_b64decode
from logging import getLogger

from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.utils import PdfReadError

from odoo import _, models
from odoo.exceptions import UserError

logger = getLogger(__name__)


class PDFReport(models.Model):
    _inherit = "ir.actions.report"

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        result = super(PDFReport, self)._post_pdf(
            save_in_attachment, pdf_content=pdf_content, res_ids=res_ids
        )
        if not "sale_dimension_split.orden_de_trabajo_template" == self.report_name:
            return result
        if result:
            product_ids = self.env['sale.order'].search([('id','in',res_ids)]).mapped('order_line.sale_line_bom_ids.product_id')
            product_tmpl_ids = product_ids.mapped('product_tmpl_id')
            attachments = self.env["mrp.document"].search(
                [
                    "|",
                    "&",
                    ("res_model", "=", "product.product"),
                    ("res_id", "in", product_ids.ids),
                    "&",
                    ("res_model", "=", "product.template"),
                    ("res_id", "in", product_tmpl_ids.ids),
                ]
            ).mapped('datas')
            
            if len(attachments) == 0: return result

            doc = PdfFileReader(io.BytesIO(result))
            pdf = PdfFileWriter()
            for attach in  attachments:
                try:
                    attach = urlsafe_b64decode(attach)
                except BaseException:
                    attach = urlsafe_b64decode(attach + b"===")
                pdf_attach = PdfFileReader(io.BytesIO(attach))
                if pdf_attach.isEncrypted:
                    try:
                        pdf_attach.decrypt("")
                    except (NotImplementedError, Exception) as e:
                        pdf_attach = None
                        msg = _(
                            "Some Attachment PDF document has security restrictions. Can not read or decrypt it!: "
                        )
                        msg += str(e)
                        logger.warning(msg)
                        raise UserError(msg)
                for page in doc.pages:
                    pdf.addPage(page)
                if pdf_attach:
                    for page in pdf_attach.pages:
                        pdf.addPage(page)
            result = io.BytesIO()
            pdf.write(result)
            return result.getvalue()

        return result
