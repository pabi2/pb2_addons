# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


def related_import_je(session, thejob):
    res_id = thejob.args[1]
    action = {
        'name': _("Import Journal Entries"),
        'type': 'ir.actions.act_window',
        'res_model': 'pabi.import.journal.entries',
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': res_id,
    }
    return action


@job
@related_action(action=related_import_je)
def action_import_je_split_entries(session, model_name, res_id):
    """ Job Function, that calls underlineing function """
    try:
        session.pool[model_name].split_entries(session.cr, session.uid,
                                               [res_id], session.context)
        import_je = session.pool[model_name].browse(session.cr, session.uid,
                                                    res_id)
        # Return Message to Job Queue
        return _('Successful Split Entries for %s') % import_je.name
    except Exception, e:
        raise RetryableJobError(e)


class PabiImportJournalEntries(models.Model):
    _inherit = 'pabi.import.journal.entries'

    # Add extra fields / function (do not change)
    async_process = fields.Boolean(
        string='Split entries in background?',
        default=False,
    )
    job_id = fields.Many2one(
        'queue.job',
        string='Job',
        compute='_compute_job_uuid',
    )
    uuid = fields.Char(
        string='Job UUID',
        compute='_compute_job_uuid',
    )

    @api.multi
    def _compute_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_import_je_split_entries',
                 self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.job_id = jobs and jobs[0] or False
            rec.uuid = jobs and jobs[0].uuid or False
        return True

    # End required extra fields / function

    @api.multi
    def split_entries(self):
        """ Inherit existing function, and test if it async_process is True """
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(PabiImportJournalEntries, self).split_entries()
        # Enqueue
        if self.async_process:
            if self.job_id:  # Job already started, check at My Jobs menu
                message = _('Import JE - Split Entries')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Import JE - Split Entries(s)' % self.name
            uuid = action_import_je_split_entries.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('sample_pabi_async_process.'
                                          'import_je_split_entries')
        else:
            return super(PabiImportJournalEntries, self).split_entries()
