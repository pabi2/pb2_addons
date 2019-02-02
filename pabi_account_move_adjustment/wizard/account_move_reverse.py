# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError

@job
def action_reverse_async_process(session, model_name, res_id, move_ids):
    try:
        ctx = session.context.copy()
        ctx.update({'active_ids' : move_ids})
        res = session.pool[model_name].action_reverse_backgruond(
            session.cr, session.uid, [res_id], ctx)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)
    
class AccountMoveReverse(models.TransientModel):
    _inherit = 'account.move.reverse'


    def get_active_ids(self):
        active_ids = self._context.get('active_ids') or False
        if active_ids:
            return ','.join(str(x) for x in active_ids)
        else:
            return False
        
    reverse_temp_acive_ids = fields.Text(
        string='Active Ids',
        default=get_active_ids
    )
    
    reverse_job_id = fields.Many2one(
        'queue.job',
        string='Reverse Job',
        compute='_compute_reverse_job_uuid',
    )
    reverse_uuid = fields.Char(
        string='Reverse Job UUID',
        compute='_compute_reverse_job_uuid',
    )

    @api.multi
    def _compute_reverse_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_reverse_async_process', 'account.move', rec.reverse_temp_acive_ids)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.reverse_job_id = jobs and jobs[0] or False
            rec.reverse_uuid = jobs and jobs[0].uuid or False
        return True
    
    @api.multi
    def action_reverse_backgruond(self):
        assert 'active_ids' in self._context, "active_ids missing in context"
        active_ids = self._context.get('active_ids') or False
        if self._context.get('reverse_async_process', False):
            self.ensure_one()
            if self._context.get('job_uuid', False):  # Called from @job
                return self.action_reverse()
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'account.move.reverse - Reverse Entries'
            uuid = action_reverse_async_process.delay(
                session, 'account.move.reverse', self.id, active_ids, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            #job.process_id = self.env.ref('pabi_async_process.'
            #                              'confirm_pos_order')
        else:
            return self.action_reverse()
        
    @api.multi
    def action_reverse(self):
        self.ensure_one()
        result = super(AccountMoveReverse, self).action_reverse()
        ctx = ast.literal_eval(result['context'])
        ctx.update({'direct_create': True})  # To ensure refresh dimension
        result['context'] = ctx
        move_id = self._context.get('active_id')
        move = self.env['account.move'].browse(move_id)
        if move and move.doctype == 'adjustment':
            journal_budget = self.env.ref('pabi_account_move_adjustment.'
                                          'journal_adjust_budget')
            journal_no_budget = self.env.ref('pabi_account_move_adjustment.'
                                             'journal_adjust_no_budget')
            action = False
            if move.journal_id == journal_budget:
                action = self.env.ref('pabi_account_move_adjustment.'
                                      'action_journal_adjust_budget')
            if move.journal_id == journal_no_budget:
                action = self.env.ref('pabi_account_move_adjustment.'
                                      'action_journal_adjust_no_budget')
            if action:
                new_result = action.read()[0]
                domain = ast.literal_eval(new_result['domain']) + \
                    ast.literal_eval(result['domain'])
                new_result['domain'] = domain
                new_result['name'] = result['name']
                new_result['context'] = result['context']
                result = new_result
        return result
