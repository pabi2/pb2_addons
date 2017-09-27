# -*- coding: utf-8 -*-
from openerp import api, _
from openerp.exceptions import RedirectWarning


class PabiAsync(object):

    @api.model
    def _check_queue(self, enqueue_method, doc_name=False):
        task = "%s('%s', %s)" % (enqueue_method, self._name, self.id)
        jobs = self.env['queue.job'].\
            search([('func_string', 'like', task),
                    ('state', 'not in', ('done', 'failed'))])
        if len(jobs) > 0:
            action = self.env.ref('pabi_async_process.action_my_queue_job')
            message = False
            if doc_name:
                message = _('This action is enqueued for %s') % (doc_name,)
            else:
                message = _('This action is enqueued')
            raise RedirectWarning(message, action.id, _('Go to My Jobs'))
