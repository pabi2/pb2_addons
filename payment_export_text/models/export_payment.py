# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval as eval


class PaymentExport(models.Model):
    _inherit = 'payment.export'

    @api.model
    def _prepare_data(self):
        config_id = self.env['payment.export.config'].search([])
        eval_context = self._get_eval_context()
        
        data_list = []
        # for header part
        header_config_lines = config_id.header_config_line_ids.read(
            ['sequence', 'field_code', 'length', 'mandatory', 'notes'])
        for line in header_config_lines:
            if line['field_code']:
                eval(line['field_code'], eval_context, mode="exec", nocopy=True)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['notes'] and line['notes'] or ''
                line.update({'value': value})
        header_config_lines.insert(0, {'length': 3,
                                    'mandatory': True,
                                    'sequence': 0,
                                    'field_code': '',
                                    'id': 0,
                                    'value': '003'})
        data_list.append(header_config_lines)
        # for Invoice Detail part
        invoice_detail_config_lines = config_id.invoice_config_line_ids.read(
            ['sequence', 'field_code', 'length', 'mandatory', 'notes'])
        for line in invoice_detail_config_lines:
            if line['field_code']:
                eval(line['field_code'], eval_context, mode="exec", nocopy=True)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['notes'] and line['notes'] or ''
                line.update({'value': value})
        if invoice_detail_config_lines:
            invoice_detail_config_lines.insert(0, {'length': 3,
                                        'mandatory': True,
                                        'sequence': 0,
                                        'field_code': '',
                                        'id': 0,
                                        'value': '006'})
            data_list.append(invoice_detail_config_lines)
        # for footer part
        footer_config_lines = config_id.footer_config_line_ids.read(
            ['sequence', 'field_code', 'length', 'mandatory', 'notes'])
        for line in footer_config_lines:
            if line['field_code']:
                eval(line['field_code'], eval_context, mode="exec", nocopy=True)
                value = eval_context.get('value', False)
                line.update({'value': value})
            else:
                value = line['notes'] and line['notes'] or ''
                line.update({'value': value})
        footer_config_lines.insert(0, {'length': 3,
                                    'mandatory': True,
                                    'sequence': 0,
                                    'field_code': '',
                                    'id': 0,
                                    'value': '100'})
        data_list.append(footer_config_lines)
        return data_list
