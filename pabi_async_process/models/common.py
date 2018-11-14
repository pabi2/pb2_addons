# -*- coding: utf-8 -*-
from openerp import api, _
from openerp.exceptions import RedirectWarning, ValidationError


class PabiAsync(object):

    @api.model
    def _check_queue(self, task_name, desc=False, type='always'):
        """ Checking Type
        'never' : No checking on task, simply show the RedirectWarning to myJob
            - no check in any case
        'always' : Check any duplicated task (regardless of who starts it)
            - for document with document id
        'mytask' : Check duplicate task on the same user only
            - for reports
        """
        if type and type not in ['never', 'always', 'mytask']:
            raise ValidationError(_('Wrong job checking type!'))

        if type == 'never':
            jobs = self._get_running_jobs(task_name, type)
            self._cr.commit()
            uuid = jobs[0].uuid
        elif type in ['always', 'mytask']:
            jobs = self._get_running_jobs(task_name, type)
            if not jobs:
                raise ValidationError(_('Something wrong, job not created!'))
            if len(jobs) == 1:  # 1 Job ok, we can commit. Else, not create.
                self._cr.commit()
            uuid = jobs[0].uuid
        # Show RedirectWarning Message
        message = False
        if desc:
            message = _('This action is enqueued -- %s') % desc
        else:
            message = _('This action is enqueued')
        if uuid:
            message += '\nUUID: %s' % uuid
        action = self.env.ref('pabi_utils.action_my_queue_job')
        raise RedirectWarning(message, action.id, _('Go to My Jobs'))

    @api.model
    def _get_running_jobs(self, task_name, type=type):
        dom = [('func_string', 'like', task_name),
               ('state', 'not in', ('done', 'failed'))]
        order = 'id desc'
        if type == 'never':
            order = 'id desc'  # For case never, latest first
        if type == 'always':
            dom = dom
            order = 'id'
        if type == 'mytask':
            dom.append(('user_id', '=', self._uid))  # My job only
            order = 'id'
        jobs = self.env['queue.job'].search(dom, order=order)
        return jobs
