# -*- coding: utf-8 -*-
import os
import base64
import tempfile
from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval as eval


class DocumentExportParser(models.TransientModel):
    _inherit = 'document.export.parser'

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

    @api.model
    def _prepare_data(self):
        config_id = self.config_id
        if not config_id:
            raise Warning(_('Please configure payment export in settings.'))
        config_fields_to_read = ['sequence', 'field_code',
                                 'length', 'mandatory',
                                 'default_value', 'model_id',
                                 'notes']
        active_model = self._context.get('active_model', '')
        active_model =\
            self.env['ir.model'].search([('model', '=', active_model)])
        active_id = self._context.get('active_id', False)
        payment_export_record = self.env[active_model.model].browse(active_id)
        data_list = []
        # for header part
        header_config_lines =\
            config_id.header_config_line_ids.read(config_fields_to_read)
        for line in header_config_lines:
            if line['field_code']:
                model = active_model.id
                if line.get('model_id', []):
                    model = line['model_id'][0]
                eval_context = self._get_eval_context(model, active_id)
                eval(line['field_code'], eval_context,
                     mode="exec", nocopy=True)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['default_value'] and line['default_value'] or ''
                line.update({'value': value})
        header_config_lines.insert(0, {'length': 3,
                                       'mandatory': True,
                                       'sequence': 0,
                                       'field_code': '',
                                       'id': 0,
                                       'value': '001'})
        data_list.append(header_config_lines)
        # for Line Detail part
        if payment_export_record.line_ids:
            for export_line in payment_export_record.line_ids:
                line_detail_config_lines =\
                    config_id.detail_config_line_ids.read(
                                                          config_fields_to_read
                                                          )
                for line in line_detail_config_lines:
                    model_id = active_model.id
                    if line.get('model_id', []):
                        model_id = line['model_id'][0]
                    if model_id == active_model.id:
                        eval_context = self._get_eval_context(
                            active_model.id, active_id)
                    else:
                        eval_context = self._get_eval_context(
                            model_id, export_line.id)
                    if line['field_code']:
                        eval(line['field_code'], eval_context,
                             mode="exec", nocopy=True)
                        value = eval_context.get('value', False)
                        line.update({'value': value})
                    else:
                        value = line['default_value'] and\
                            line['default_value'] or ''
                        line.update({'value': value})
                if line_detail_config_lines:
                    line_detail_config_lines.insert(0, {'length': 3,
                                                        'mandatory': True,
                                                        'sequence': 0,
                                                        'field_code': '',
                                                        'id': 0,
                                                        'value': '003'})
                data_list.append(line_detail_config_lines)
#         # for Invoice Detail part
#         invoice_detail_config_lines =\
#             config_id.invoice_config_line_ids.read(config_fields_to_read)
#         for line in invoice_detail_config_lines:
#             if line['field_code']:
#                 eval(line['field_code'], eval_context,
#                      mode="exec", nocopy=True)
#                 value = eval_context.get('value', False)
#                 line.update({'value': value})
#             else:
#                 value = line['default_value'] and line['default_value'] or ''
#                 line.update({'value': value})
#         if invoice_detail_config_lines:
#             invoice_detail_config_lines.insert(0, {'length': 3,
#                                                    'mandatory': True,
#                                                    'sequence': 0,
#                                                    'field_code': '',
#                                                    'id': 0,
#                                                    'value': '006'})
#             data_list.append(invoice_detail_config_lines)

        # for footer part
        footer_config_lines =\
            config_id.footer_config_line_ids.read(config_fields_to_read)
        for line in footer_config_lines:
            if line['field_code']:
                model = active_model.id
                if line.get('model_id', []):
                    model = line['model_id'][0]
                eval_context = self._get_eval_context(model, active_id)
                eval(line['field_code'], eval_context,
                     mode="exec", nocopy=True)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['default_value'] and line['default_value'] or ''
                line.update({'value': value})
        footer_config_lines.insert(0, {'length': 3,
                                       'mandatory': True,
                                       'sequence': 0,
                                       'field_code': '',
                                       'id': 0,
                                       'value': '100'})
        data_list.append(footer_config_lines)
        return data_list
