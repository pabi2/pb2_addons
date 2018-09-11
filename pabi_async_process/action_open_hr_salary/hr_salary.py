# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_hr_salary(session, thejob):
    salary_id = thejob.args[1]
    action = {
        'name': _('Salary Expense'),
        'type': 'ir.actions.act_window',
        'res_model': 'hr.salary.expense',
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': salary_id,
    }
    return action


@job
@related_action(action=related_hr_salary)
def action_open_hr_salary(session, model_name, res_id):
    try:
        session.pool[model_name].action_open(session.cr, session.uid,
                                             [res_id], session.context)
        salary = session.pool[model_name].browse(session.cr, session.uid,
                                                 res_id)
        return {'salary_id': salary.id}
    except Exception, e:
        raise FailedJobError(e)


class HRSalaryExpense(PabiAsync, models.Model):
    _inherit = 'hr.salary.expense'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=True,
    )

    @api.multi
    def action_open(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(HRSalaryExpense, self).action_open()
        # Enqueue
        if self.async_process and self.state != 'open':
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Generate Entries - Salary Expense %s' % self.number
            uuid = action_open_hr_salary.delay(session, self._name, self.id,
                                               description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'hr_salary')
            # Checking for running task, use the same signature as delay()
            task_name = "%s('%s', %s)" % \
                ('action_open_hr_salary', self._name, self.id)
            self._check_queue(task_name, desc=description, type='always')
        else:
            return super(HRSalaryExpense, self).action_open()
