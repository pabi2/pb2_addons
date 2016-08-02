# -*- coding: utf-8 -*-
import os
import base64
import tempfile
from openerp import api, fields, models, _


class PaymentExportParser(models.TransientModel):
    _inherit = 'payment.export.parser'

    file_type = fields.Selection(
        selection_add=[('txt', 'Text')],
    )

    @api.model
    def _prepare_data(self):
        datas = [
            [
               {'sr_no': 1, 'field_name': 'record_type', 'length': 3, 'mandatory': True, 'value': '001'},
               {'sr_no': 2, 'field_name': 'company_id.name', 'length': 20, 'mandatory': True, 'value': 'NSTDA'},
               {'sr_no': 3, 'field_name': 'company_id.vat', 'length': 15, 'mandatory': True, 'value': 994000165668},
               {'sr_no': 4, 'field_name': 'company_id.debit_account', 'length': 20, 'mandatory': True, 'value': '803000017'},
               {'sr_no': 5, 'field_name': 'company_id.batch_ref', 'length': 25, 'mandatory': True, 'value': 'B_16092015160320'},
               {'sr_no': 6, 'field_name': 'company_id.batch_broadcast_message', 'length': 5, 'mandatory': False, 'value': 'msg'},
               {'sr_no': 7, 'field_name': 'file_date', 'length': 8, 'mandatory': True, 'value': '16092015'},
               {'sr_no': 8, 'field_name': 'file_timestamp', 'length': 6, 'mandatory': True, 'value': '160320'},
            ],
        ]
        return datas

    @api.model
    def _generate_file_attachment(self, line_text):
        payment_id = self.env.context.get('active_id', False)
        payment_model = self.env.context.get('active_model', '')
        path = tempfile.mktemp('.' + self.file_type)
        temp = file(path, 'wb')
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
