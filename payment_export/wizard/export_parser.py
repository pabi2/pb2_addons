# -*- coding: utf-8 -*-
import os
import base64
import tempfile
from operator import itemgetter
from openerp import api, fields, models, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)

DELIMITER = '~'


class PaymentExportParser(models.TransientModel):
    _name = 'payment.export.parser'
    _description = 'Export Payment'

    file_type = fields.Selection(
        selection=[],
        string='File Type',
        required=True,
    )

    @api.model
    def _validate_data(self, data_list):
        if not data_list:
            raise Warning(_('There is nothing to validate'))
        invalid_data_list = [d['id'] for d in data_list
                             if d['mandatory'] and not d['value']]
        if invalid_data_list:
            raise Warning(_('Please enter valid data for '))
        return True

    @api.model
    def _generate_text_line(self, data_list):
        line_text = False
        for data in data_list:
            value = data['value']
            if not isinstance(value, basestring):
                value = str(value)
            if len(value) > data['length']:
                value = value[:data['length']]
            if not line_text:
                line_text = value
            else:
                line_text = line_text + DELIMITER + value
        return line_text and line_text + '\n' or False

    @api.model
    def _generate_file_attachment(self, line_text):
        attachment_id = False
        raise Warning(_('Method not implemented!'))


    @api.multi
    def export_file(self):
        self.ensure_one()
        payment_id = self.env.context.get('active_id', False)
        payment_model = self.env.context.get('active_model', '')
        payment = self.env[payment_model].browse(payment_id)
        final_line_text = False
        datas = payment._prepare_data()

        for data_list in datas:
            self._validate_data(data_list)
            data_list = sorted(data_list, key=itemgetter('sequence'))
            line_text = self._generate_text_line(data_list)
            if not final_line_text:
                final_line_text = line_text
            else:
                final_line_text += line_text

        attachement_id = self._generate_file_attachment(final_line_text)
        return attachement_id
