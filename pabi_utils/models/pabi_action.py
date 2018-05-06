# -*- coding: utf-8 -*-
from ast import literal_eval
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_result(session, thejob):
    """ Open up result of this process """
    job = session.env['queue.job'].search([('uuid', '=', thejob._uuid)])
    return_action = thejob.args[3]
    res_ids = literal_eval(job.res_ids)
    if not res_ids:
        raise ValidationError(_('No results form this process'))
    # Specified action
    if return_action and job.res_model:
        result = session.env.ref(return_action).read()[0]
        if result.get('res_model') != job.res_model:
            raise ValidationError(
                _('Wrong action provided: %s!') % return_action)
        result.update({'domain': [('id', 'in', res_ids)]})
        return result
    # Default action
    return {
        'type': 'ir.actions.act_window',
        'res_model': job.res_model,
        'view_mode': 'tree,form',
        'view_type': 'form',
        'domain': [('id', 'in', res_ids)],
    }


@job(default_channel='root.pabi_action')
@related_action(action=related_result)
def pabi_action_job(session, model_name, func_name, kwargs, return_action):
    try:
        PabiAction = session.env[model_name]
        records = getattr(PabiAction, func_name)(**kwargs)
        # Write result back to job
        job_uuid = session.context.get('job_uuid')
        job = session.env['queue.job'].search([('uuid', '=', job_uuid)])
        job.write({'res_model': records._name,
                   'res_ids': str(records.ids)})
        # Result Description
        result = _('Successfully execute process')
        return result
    except Exception, e:
        raise FailedJobError(e)


class PabiAction(models.AbstractModel):
    """ To be extended by action wizard, to simplily background job  """
    _name = 'pabi.action'
    # Common Fields
    res_ids = fields.Char(
        string='Result IDs',
        readonly=True,
        help="String representative of id list of record newly created",
    )
    res_model = fields.Char(
        string='Result Model',
        readonly=True,
        help="Model of the imported record",
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
        help="Job queue unique identifiers",
    )

    @api.multi
    def pabi_action(self, process_xml_id, job_desc, func_name, **kwargs):
        self.ensure_one()
        # Enqueue
        if self.async_process:
            session = ConnectorSession(self._cr, self._uid, self._context)
            return_action = self._context.get('return_action', False)
            uuid = pabi_action_job.delay(session, self._name,
                                         func_name, kwargs,
                                         return_action,
                                         description=job_desc)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref(process_xml_id)
            self.write({'state': 'get', 'uuid': uuid})
        else:
            # Call prepared function form the extended class
            records = getattr(self, func_name)(**kwargs)
            self.write({'state': 'get',
                        'res_model': records._name,
                        'res_ids': str(records.ids), })
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
        if not res_ids:
            raise ValidationError(_('No results form this process'))
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
