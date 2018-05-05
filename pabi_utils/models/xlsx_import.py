# -*- coding: utf-8 -*-
from ast import literal_eval
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError, RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


@job(default_channel='root.xlsx_import')
def get_import_job(session, ctx, model_name, res_id, att_id):
    try:
        # Get attachment
        wizard = session.env[model_name].browse(res_id)
        attachment = session.env['ir.attachment'].browse(att_id)
        Import = session.env['import.xlsx.template'].with_context(ctx)
        record = Import.import_template(attachment.datas,
                                        wizard.template_id,
                                        wizard.res_model)
        # Link attachment to job queue
        job_uuid = session.context.get('job_uuid')
        job = session.env['queue.job'].search([('uuid', '=', job_uuid)],
                                              limit=1)
        # Get init time
        date_created = fields.Datetime.from_string(job.date_created)
        ts = fields.Datetime.context_timestamp(job, date_created)
        init_time = ts.strftime('%d/%m/%Y %H:%M:%S')
        # Description
        desc = 'INIT: %s\n> UUID: %s' % (init_time, job_uuid)
        attachment.write({
            'name': '%s_%s' % (record.display_name, attachment.name),
            'parent_id': session.env.ref('pabi_utils.dir_spool_import').id,
            'description': desc, })
        return _('File imported successfully')
    except Exception, e:
        raise FailedJobError(e)


class XLSXImport(models.TransientModel):
    """ This class use import.xlsx.template, allow multi files import  """
    _name = 'xlsx.import'

    template_id = fields.Many2one(
        'ir.attachment',
        string='Template',
        required=True,
        ondelete='set null',
        domain="[('res_model', '=', res_model),"
        "('res_id', '=', False), ('res_name', '=', False)]"
    )
    domain_template_ids = fields.Many2many(
        'ir.attachment',
        string='Domain Templates',
        help="template_id's domain. If False, no domain",
    )
    res_ids = fields.Char(
        string='Result IDs',
        readonly=True,
        help="String representative of id list of record newly created",
    )
    res_names = fields.Char(
        string='Result Records',
        readonly=True,
        help="String representative of newly created record names",
    )
    res_model = fields.Char(
        string='Result Model',
        readonly=True,
        help="Model of the imported record",
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'xlsx_import_attachment_rel',
        'xlsx_import_id', 'attachment_id',
        string='Import File(s)',
        required=True,
        help="You can select multiple files to import.",
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
    uuids = fields.Char(
        string='UUIDs',
        readonly=True,
        help="Job queue unique identifiers",
    )

    @api.model
    def default_get(self, fields):
        res_model = self._context.get('active_model', False)
        template_dom = [('res_model', '=', res_model),
                        ('parent_id', '!=', False)]
        template_fname = self._context.get('template_fname', False)
        if template_fname:  # Specific template
            template_dom.append(('datas_fname', '=', template_fname))
        templates = self.env['ir.attachment'].search(template_dom)
        if not templates:
            raise ValidationError(_('No template found!'))
        defaults = super(XLSXImport, self).default_get(fields)
        for template in templates:
            if not template.datas:
                act = self.env.ref('document.action_document_directory_tree')
                raise RedirectWarning(
                    _('File "%s" not found in template, %s.') %
                    (template.datas_fname, template.name),
                    act.id, _('Set Templates'))
        defaults['template_id'] = len(templates) == 1 and template.id or False
        defaults['res_model'] = res_model
        defaults['domain_template_ids'] = templates.ids
        return defaults

    @api.multi
    def action_import_xlsx(self):
        self.ensure_one()
        file_names = self.attachment_ids.mapped('datas_fname')
        if len(file_names) != len(list(set(file_names))):
            raise ValidationError(_('Duplicated import files!'))
        # Enqueue
        if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'XLSX Import - %s' % self.res_model
            uuids = []
            ctx = self._context.copy()
            del ctx['params']  # If not removed, job is not readable by queue
            for attachment in self.attachment_ids:
                uuid = get_import_job.delay(session, ctx,
                                            self._name, self.id, attachment.id,
                                            description=description)
                uuids.append(uuid)
                # Move file to attach to queue.job
                job = Job.search([('uuid', '=', uuid)], limit=1)
                attachment.write({
                    'res_model': 'queue.job',
                    'res_id': job.id,
                    'user_id': job.user_id.id, })
            self.write({'state': 'get', 'uuids': ', '.join(uuids)})
        else:
            Import = self.env['import.xlsx.template']
            records = []
            for import_file in self.attachment_ids.mapped('datas'):
                records.append(Import.import_template(import_file,
                                                      self.template_id,
                                                      self.res_model))
            res_ids = []
            names = []
            for rec in records:
                res_ids.append(rec.id)
                names.append(rec.display_name)
            self.write({'state': 'get',
                        'res_ids': str(res_ids),
                        'res_names': ', '.join(names)})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def action_open_result(self):
        self.ensure_one()
        res_ids = literal_eval(self.res_ids)
        # Specified action
        if self._context.get('return_action', False):
            action = self.env.ref(self._context['return_action'])
            result = action.read()[0]
            if result.get('res_model') != self.res_model:
                raise ValidationError(_('Wrong action provided: %s!') %
                                      self._context['return_action'])
            result.update({'domain': [('id', 'in', res_ids)]})
            return result
        # Default action
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', res_ids)],
        }
