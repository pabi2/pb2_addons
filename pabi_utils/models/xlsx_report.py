# -*- coding: utf-8 -*-
import base64
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


@job(default_channel='root.xlsx_report')
def get_report_job(session, model_name, res_id, lang=False):
    try:
        # Update context
        ctx = session.context.copy()
        if lang:
            ctx.update({'lang': lang})
        out_file, out_name = session.pool[model_name].get_report(
            session.cr, session.uid, [res_id], ctx)
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


@job(default_channel='root.xlsx_report')
def action_export_excel(session, model_name, res_id, report_name, lang=False):
    try:
        report = session.env['ir.actions.report.xml'].search([
            ('report_name', '=', report_name),
            ('report_type', '=', 'xlsx'),
        ])
        # Update context
        out_file, report_type = report.with_context(
            {'lang': lang}).render_report([res_id], report_name, {})
        out_file = base64.b64encode(out_file)
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
        out_name = report.name.replace(' ', '')
        out_name = '%s_%s' % (out_name, ts.strftime('%Y%m%d_%H%M%S'))
        session.env['ir.attachment'].create({
            'name': '%s.xlsx' % out_name,
            'datas': out_file,
            'datas_fname': '%s.xlsx' % out_name,
            'res_model': 'queue.job',
            'res_id': job.id,
            'type': 'binary',
            'parent_id': session.env.ref('pabi_utils.dir_spool_report').id,
            'description': desc,
            'user_id': job.user_id.id,
        })
        # Result Description
        result = _('Successfully created excel report : %s.xlsx') % out_name
        return result
    except Exception, e:
        raise FailedJobError(e)


class XLSXReport(models.AbstractModel):
    """ Common class for xlsx reporting wizard """
    _name = 'xlsx.report'

    name = fields.Char(
        string='File Name',
        readonly=True,
        size=500,
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
        size=500,
        help="Job queue unique identifier",
    )
    to_csv = fields.Boolean(
        string='Convert to CSV?',
        default=False,
    )
    csv_delimiter = fields.Char(
        string='CSV Delimiter',
        size=1,
        default=',',
        required=True,
        help="Optional for CSV, default is comma.",
    )
    csv_extension = fields.Char(
        string='CSV File Extension',
        size=5,
        default='csv',
        required=True,
        help="Optional for CSV, default is .csv"
    )
    csv_quote = fields.Boolean(
        string='CSV Quoting',
        default=True,
        help="Optional for CSV, default is full quoting."
    )
    specific_template = fields.Selection(
        [],
        string='Template',
        help="Optional field, if derived report want to have selection",
    )

    @api.multi
    def get_report(self):
        self.ensure_one()
        Export = self.env['export.xlsx.template']
        Attachment = self.env['ir.attachment']
        template = []
        # By default, use template by model
        if self.specific_template:
            template = self.env.ref(self.specific_template, [])
        else:
            template = Attachment.search([('res_model', '=', self._name)])
        if len(template) != 1:
            raise ValidationError(
                _('No one template selected for "%s"') % self._name)
        return Export._export_template(
            template, self._name, self.id,
            to_csv=self.to_csv,
            csv_delimiter=self.csv_delimiter,
            csv_extension=self.csv_extension,
            csv_quote=self.csv_quote)

    @api.multi
    def button_export_xlsx(self, report_name=None):
        self.ensure_one()
        if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Excel Report - %s' % (self._name)
            uuid = action_export_excel.delay(
                session, self._name, self.id, report_name,
                description=description,
                lang=session.context.get('lang', False))
            job = Job.search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_utils.xlsx_report')
            self.write({'state': 'get', 'uuid': uuid})
            result = {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        else:
            result = self.env['report'].get_action(self, report_name)
        return result

    @api.multi
    def action_get_report(self):
        self.ensure_one()
        # Enqueue
        if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Excel Report - %s' % (self._name, )
            uuid = get_report_job.delay(
                session, self._name, self.id, description=description,
                lang=session.context.get('lang', False))
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
