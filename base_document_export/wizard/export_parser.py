# -*- coding: utf-8 -*-
import time
import datetime
import dateutil
import openerp
from operator import itemgetter
from openerp import workflow
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

DELIMITER = ''


class DocumentExportParser(models.TransientModel):
    _name = 'document.export.parser'
    _description = 'Export Document'

    file_type = fields.Selection(
        selection=[],
        string='File Type',
        required=True,
    )
    config_id = fields.Many2one(
        'document.export.config',
        string='Export Format',
        required=False,
        ondelete='set null'
    )

    @api.model
    def default_get(self, fields):
        res = super(DocumentExportParser, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        export = self.env[active_model].browse(active_id)
        if export.journal_id:
            res['file_type'] = export.journal_id.file_type
        return res

    @api.model
    def _validate_data(self, data_list):
        if not data_list:
            raise ValidationError(_('There is nothing to validate'))
        invalid_data_list = [d['notes'] for d in data_list
                             if d['mandatory'] and not d['value']]
        if invalid_data_list:
            raise ValidationError(_('Please enter valid data for: %s'
                                  % (',\n'.join(invalid_data_list))))
        return True

    @api.model
    def _generate_text_line(self, data_list):
        joining_delimiter = DELIMITER
        if self.config_id and self.config_id.delimiter_symbol:
            joining_delimiter = self.config_id.delimiter_symbol
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
                line_text = line_text + joining_delimiter + value
        return line_text and line_text + '\n' or False

    @api.model
    def _generate_file_attachment(self, line_text):
        # attachment_id = False
        raise ValidationError(_('Method not implemented!'))

    @api.model
    def _get_eval_context(self, active_model_id, active_id):
        """ Prepare the context used when evaluating python code, like the
        condition or code server actions.

        :returns: dict -- evaluation context given to (safe_)eval """
        active_model = str(self._model)
        if active_model_id:
            active_model = self.env['ir.model'].browse(active_model_id).model
        env = openerp.api.Environment(self._cr, self._uid, self._context)
        model = env[active_model]
        obj = model.browse(active_id)
        eval_context = {
            # python libs
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            # orm
            'env': env,
            'model': model,
            'workflow': workflow,
            # Exceptions
            'ValidationError': openerp.exceptions.ValidationError,
            # record
            # deprecated and define record (active_id) and records (active_ids)
            'object': obj,
            'obj': obj,
            # Deprecated use env or model instead
            'self': obj,
            'pool': self.pool,
            'cr': self._cr,
            'uid': self._uid,
            'context': self._context,
            'user': env.user,
        }
        return eval_context

    @api.model
    def _prepare_data(self):
        raise ValidationError(_('Method not implemented!'))

    @api.multi
    def export_file(self):
        self.ensure_one()
        # document_id = self.env.context.get('active_id', False)
        # document_model = self.env.context.get('active_model', '')
        # document = self.env[document_model].browse(document_id)
        final_line_text = False
        datas = self._prepare_data()
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
