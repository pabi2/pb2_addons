# -*- coding: utf-8 -*-
import re
import base64

import openerp
from openerp import models, fields, api, _
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


@job
def action_run_tax_report(session, data, format):
    try:
        # Render Report
        rpt_name = 'pabi_th_tax_report.%s' % data['report_name']
        report = session.env.ref(rpt_name)
        data = data['datas']
        data['model'] = 'account.tax.report'  # model is required, even sql rpt
        result, _x = openerp.report.render_report(session.cr, session.uid, [],
                                                  report.report_name, data)
        # Make attachment and link ot job queue
        job_uuid = session.context.get('job_uuid')
        job = session.env['queue.job'].search([('uuid', '=', job_uuid)],
                                              limit=1)
        result = base64.b64encode(result)
        file_name = 'VAT Report'
        file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
        file_name += format == 'pdf' and '.pdf' or '.xls'
        # Get init time
        date_created = fields.Datetime.from_string(job.date_created)
        ts = fields.Datetime.context_timestamp(job, date_created)
        init_time = ts.strftime('%d/%m/%Y %H:%M:%S')
        # Description
        desc = 'INIT: %s\n> UUID: %s' % (init_time, job_uuid)
        session.env['ir.attachment'].create({
            'name': file_name,
            'datas': result,
            'datas_fname': file_name,
            'res_model': 'queue.job',
            'res_id': job.id,
            'type': 'binary',
            'parent_id': session.env.ref('pabi_utils.dir_spool_report').id,
            'description': desc,
            'user_id': job.user_id.id,
        })
        return _('Tax Report created successfully')
    except Exception, e:
        raise FailedJobError(e)  # Queue Error


class AccountTaxReportWizard(PabiAsync, models.TransientModel):
    _inherit = 'account.tax.report.wizard'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )

    @api.multi
    def run_report(self):
        # Enqueue
        if self.async_process:
            data = super(AccountTaxReportWizard, self).run_report()
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Print Tax Report' % self.tax_id.name
            uuid = action_run_tax_report.delay(session, data,
                                               self.print_format,
                                               description=description)
            # Checking for running task, use the same signature as delay()
            task_name = "%s(%s, u'%s')" % \
                ('action_run_tax_report', data, self.print_format)
            self._check_queue(task_name, desc=description,
                              type='never', uuid=uuid)
        else:
            return super(AccountTaxReportWizard, self).run_report()
