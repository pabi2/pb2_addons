# -*- coding: utf-8 -*-
import os
import base64
import tempfile
import time
import datetime
import dateutil
import openerp
from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp import workflow


class PaymentExportParser(models.TransientModel):
    _inherit = 'payment.export.parser'

    file_type = fields.Selection(
        selection_add=[('txt', 'Text')],
    )

    @api.model
    def _generate_file_attachment(self, line_text):
        payment_id = self.env.context.get('active_id', False)
        payment_model = self.env.context.get('active_model', '')
        path = tempfile.mktemp('.' + self.file_type)
        temp = file(path, 'wb')
        line_text = line_text.encode('utf-8').strip()
        temp.write(line_text)
        result = base64.b64encode(line_text)
        (dirName, fileName) = os.path.split(path)
        attachment_id = self.env['ir.attachment'].create({
                               'name': 'payment' + '.' + self.file_type,
                               'datas': result,
                               'datas_fname': fileName,
                               'res_model': payment_model,
                               'res_id': payment_id,
                               'type': 'binary'
                              })
        temp.close()
        return attachment_id
