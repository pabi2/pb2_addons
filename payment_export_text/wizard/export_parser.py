# -*- coding: utf-8 -*-
import os
import base64
import tempfile
from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import ValidationError


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
        line_text = line_text.encode('utf-8-sig').strip()
        temp.write(line_text)
        result = base64.b64encode(line_text)
        (dirName, fileName) = os.path.split(path)
        filename = payment_model == 'payment.export' and \
            self.env[payment_model].browse(payment_id).name or 'payment'
        attachment_id = self.env['ir.attachment'].create({
            'name': filename + '.' + self.file_type,
            'datas': result,
            'datas_fname': fileName,
            'res_model': payment_model,
            'res_id': payment_id,
            'type': 'binary',
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
        data_list003 = []
        data_list006 = []
        # for header part
        header_config_lines =\
            config_id.header_config_line_ids.read(config_fields_to_read)
        for line in header_config_lines:
            if line['field_code']:
                model = active_model.id
                if line.get('model_id', []):
                    model = line['model_id'][0]
                eval_context = self._get_eval_context(model, active_id)
                #eval(line['field_code'], eval_context,
                #     mode="exec", nocopy=True)
                exec(line['field_code'], eval_context)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['default_value'] and line['default_value'] or ''
                line.update({'value': value})
        data_list.append(header_config_lines)
        # for Line Detail part
        export_lines = payment_export_record.line_ids
        
        # If defined line number max
        if config_id.line_number_max not in [False, 0] and \
                len(export_lines) > config_id.line_number_max:
            raise ValidationError(
                _('This bank allows only %s lines')
                % (config_id.line_number_max,))
        if export_lines:
            for export_line in export_lines:
                line_detail_config_lines = \
                    config_id.detail_config_line_ids.\
                    read(config_fields_to_read)
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
                        #eval(line['field_code'], eval_context,
                        #     mode="exec", nocopy=True)
                        exec(line['field_code'], eval_context)
                        value = eval_context.get('value', False)
                        line.update({'value': value})
                    else:
                        value = line['default_value'] and\
                            line['default_value'] or ''
                        line.update({'value': value})
                data_list003.append(line_detail_config_lines)

        # If use invoice_detail
        if not config_id.invoice_detail_disabled:
            voucher_lines = [x.voucher_id.line_ids for x in export_lines]
            if export_lines and voucher_lines:
                for voucher_line in voucher_lines:
                    for invoice_line in voucher_line:
                        line_invoice_detail_config_lines = config_id.invoice_detail_config_line_ids.read(config_fields_to_read)
                        for line in line_invoice_detail_config_lines:
                            model_id = active_model.id
                            if line.get('model_id', []):
                                model_id = line['model_id'][0]
                            if model_id == active_model.id:
                                eval_context = self._get_eval_context(
                                    active_model.id, active_id)
                            else:
                                eval_context = self._get_eval_context(
                                    model_id, invoice_line.id)
                            if line['field_code']:
                                #eval(line['field_code'], eval_context,
                                #     mode="exec", nocopy=True)
                                exec(line['field_code'], eval_context)
                                value = eval_context.get('value', False)
                                line.update({'value': value})
                            else:
                                value = line['default_value'] and\
                                    line['default_value'] or ''
                                line.update({'value': value})
                        data_list006.append(line_invoice_detail_config_lines)

        len_list = data_list003 if (len(data_list003) >= len(data_list006)) else data_list006
        for list in range(len(len_list)):
            data_list.append(data_list003[list-1])
            data_list.append(data_list006[list-1])

        # If not use footer
        if config_id.footer_disabled:
            return data_list
        # for footer part
        footer_config_lines = config_id.footer_config_line_ids.read(config_fields_to_read)
        for line in footer_config_lines:
            if line['field_code']:
                model = active_model.id
                if line.get('model_id', []):
                    model = line['model_id'][0]
                eval_context = self._get_eval_context(model, active_id)
                #eval(line['field_code'], eval_context,
                #     mode="exec", nocopy=True)
                exec(line['field_code'], eval_context)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['default_value'] and line['default_value'] or ''
                line.update({'value': value})
        data_list.append(footer_config_lines)
        return data_list
