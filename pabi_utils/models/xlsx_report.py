# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


@job(default_channel='root.xlsx_report')
def get_report_job(session, model_name, res_id):
    try:
        out_file, out_name = session.pool[model_name].get_report(
            session.cr, session.uid, [res_id], session.context)
        # Make attachment and link ot job queue
        job_uuid = session.context.get('job_uuid')
        job = session.env['queue.job'].search([('uuid', '=', job_uuid)],
                                              limit=1)
        # Get init time
        date_created = fields.Datetime.from_string(job.date_created)
        ts = fields.Datetime.context_timestamp(job, date_created)
        init_time = ts.strftime('%d/%m/%Y %H:%M:%S')
        # Create output report place holder
        desc = 'INIT: %s\n> UUID: %s' % (init_time, job_uuid)
        session.env['ir.attachment'].create({
            'name': out_name,
            'datas': out_file,
            'datas_fname': out_name,
            'res_model': 'queue.job',
            'res_id': job.id,
            'type': 'binary',
            'parent_id': session.env.ref('pabi_utils.dir_spool_report').id,
            'description': desc,
            'user_id': job.user_id.id,
        })
        # Result Description
        result = _('Successfully created excel report : %s') % out_name
        return result
    except Exception, e:
        raise FailedJobError(e)


class XLSXReport(models.AbstractModel):
    """ Common class for xlsx reporting wizard """
    _name = 'xlsx.report'

    name = fields.Char(
        string='File Name',
        readonly=True,
    )
    data = fields.Binary(
        string='File',
        readonly=True,
    )
    state = fields.Selection(
        [('choose', 'choose'),
         ('get', 'get')],
        default='choose',
    )
    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )
    uuid = fields.Char(
        string='UUID',
        readonly=True,
        help="Job queue unique identifier",
    )
    to_csv = fields.Boolean(
        string='Convert to CSV?',
        default=False,
    )

    @api.multi
    def get_report(self):
        self.ensure_one()
        Export = self.env['export.xlsx.template']
        Attachment = self.env['ir.attachment']
        template = Attachment.search([('res_model', '=', self._name)])
        if len(template) != 1:
            raise ValidationError(
                _('The report template "%s" must be single') % self._name)
        return Export._export_template(template, self._name,
                                       self.id,
                                       to_csv=self.to_csv)

    @api.multi
    def action_get_report(self):
        self.ensure_one()
        # Enqueue
        if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Excel Report - %s' % (self._name, )
            uuid = get_report_job.delay(
                session, self._name, self.id, description=description)
            job = Job.search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_utils.xlsx_report')
            self.write({'state': 'get', 'uuid': uuid})
        else:
            out_file, out_name = self.get_report()
            self.write({'state': 'get', 'data': out_file, 'name': out_name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
