# -*- coding: utf-8 -*-
from openerp import api, _
from openerp.exceptions import except_orm


class Common(object):

    @api.multi
    def _get_report(self, fields, report_name=False):
        data = {}
        data['form'] = self.read(fields)[0]
        for field in fields:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if self._context.copy().get('xls_export', False) and report_name:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
            }
        raise except_orm(_('Error !'), ('No report.'))
