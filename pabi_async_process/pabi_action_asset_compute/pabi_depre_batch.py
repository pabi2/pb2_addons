# -*- coding: utf-8 -*-
import time
import logging
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError

_logger = logging.getLogger(__name__)


def related_asset_depre_batch(session, thejob):
    batch_id = thejob.args[1]
    action = {
        'name': _("Asset Depre. Batch"),
        'type': 'ir.actions.act_window',
        'res_model': "pabi.asset.depre.batch",
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': batch_id,
    }
    return action


@job
@related_action(action=related_asset_depre_batch)
def action_post_asset_depre_batch(session, model_name, res_id):
    try:
        session.pool[model_name].\
            post_entries(session.cr, session.uid, [res_id], session.context)
        batch = session.pool[model_name].browse(session.cr,
                                                session.uid, res_id)
        return {'batch_id': batch.id}
    except Exception, e:
        raise FailedJobError(e)


class PabiAssetDepreBatch(models.Model):
    _name = 'pabi.asset.depre.batch'
    _order = 'id desc'
    _description = 'Asset Depreciation Compute Batch'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        help="As <period>-<run number>",
    )
    run_number = fields.Integer(
        string='Run Number',
        readonly=True,
        required=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
        required=True,
    )
    note = fields.Char(
        string='Note',
        readonly=True,
        size=500,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('posted', 'Posted'),
         ('cancel', 'Cancelled')],
        string='State',
        default='draft',
        help="* Draft: first created, user prevew\n"
        "* Posted: all journal entries posted\n"
        "* Cancelled: user choose to delete and will redo again"
    )
    move_ids = fields.One2many(
        'account.move',
        'asset_depre_batch_id',
        string='Journal Entries',
    )
    move_line_ids = fields.One2many(
        'account.move.line',
        'asset_depre_batch_id',
        string='Journal Items',
    )
    amount = fields.Float(
        string='Depreciation Amount',
        compute='_compute_amount',
    )
    move_count = fields.Integer(
        string='JE Count',
        compute='_compute_moves',
    )
    posted_move_count = fields.Integer(
        string='Posted JE Count',
        compute='_compute_moves',
    )
    # Job related fields
    async_process = fields.Boolean(
        string='Post JE in background?',
        default=True,
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
                ('action_post_asset_depre_batch', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.job_id = jobs and jobs[0] or False
            rec.uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def post_entries(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return self.action_post_entries()
        # Enqueue
        if self.async_process:
            if self.job_id:
                message = _('Post Asset Depre. Batch')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Post Asset Depre. Batch' % self.name
            uuid = action_post_asset_depre_batch.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'post_asset_depre_batch')
        else:
            return self.action_post_entries()
    # --

    @api.multi
    def _compute_moves(self):
        Move = self.env['account.move']
        for rec in self:
            rec.move_count = \
                Move.search_count([('asset_depre_batch_id', '=', rec.id)])
            rec.posted_move_count = \
                Move.search_count([('asset_depre_batch_id', '=', rec.id),
                                   ('state', '=', 'posted')])
        return True

    @api.multi
    def open_entries(self):
        self.ensure_one()
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('asset_depre_batch_id', '=', self.id)],
        }

    @api.model
    def new_batch(self, period, note):
        # Get last batch's run_number
        batch = self.search([('period_id', '=', period.id)],
                            order='run_number desc', limit=1)
        next_run = batch and (batch.run_number + 1) or 1
        new_batch = self.create({'period_id': period.id,
                                 'run_number': next_run,
                                 'note': note, })
        return new_batch

    @api.multi
    @api.depends('run_number', 'period_id')
    def _compute_name(self):
        for rec in self:
            number = str(rec.run_number)
            rec.name = '%s-%s' % (rec.period_id.name, number.zfill(2))
        return True

    @api.multi
    def delete_unposted_entries(self):
        """ For fast removal, we use SQL """
        for rec in self:
            # disable trigger, for faster execution
            self._cr.execute("""
                alter table account_move_line disable trigger all""")
            self._cr.execute("""
                alter table account_move disable trigger all""")
            # reset move_check in depre line
            self._cr.execute("""
                update account_asset_line set move_check = false
                where move_id in (
                    select id from account_move
                    where asset_depre_batch_id = %s)
            """, (rec.id, ))
            # delete from table
            self._cr.execute("""
                delete from account_move_line where asset_depre_batch_id = %s
            """, (rec.id, ))
            self._cr.execute("""
                delete from account_move where asset_depre_batch_id = %s
                and state = 'draft' and name in (null, '/')
            """, (rec.id, ))
            # enable trigger, for faster execution
            self._cr.execute("""
                alter table account_move_line enable trigger all""")
            self._cr.execute("""
                alter table account_move enable trigger all""")
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_post_entries(self):
        _logger.info("Begin action_post_entries()")
        s = time.time()
        """ For fasst post, just by pass all other checks """
        for batch in self:
            ctx = {'fiscalyear_id': batch.period_id.fiscalyear_id.id}
            Sequence = self.with_context(ctx).env['ir.sequence']
            self._cr.execute("""
                select m.id, j.sequence_id, m.ref,
                    (select max(asset_id)
                     from account_move_line where move_id = m.id) asset_id
                from account_move m
                join account_journal j on j.id = m.journal_id
                where m.asset_depre_batch_id = %s
                and m.state = 'draft' and m.name in (null, '/')
            """, (batch.id, ))
            moves = [(x[0], x[1], x[2], x[3]) for x in self._cr.fetchall()]
            # Prepare sequence for immediate update
            for move_id, sequence_id, ref, asset_id in moves:
                new_name = Sequence.next_by_id(sequence_id)
                # Update sequence
                self._cr.execute("""
                    update account_move
                    set name = %s, state = 'posted' where id = %s
                """, (new_name, move_id))
                # Update depreciation line
                self._cr.execute("""
                    update account_asset_line asl
                    set move_id = %s, move_check = true
                    where asl.id = %s
                """, (move_id, int(ref)))  # ref is the depre_line_id
                # Finally recompute asset residual value
                asset = self.env['account.asset'].browse(asset_id)
                asset._compute_depreciation()
                asset._set_close_asset_zero_value()
                self._cr.commit()
        self.write({'state': 'posted'})
        _logger.info("Done action_post_entries() in %s secs." %
                     (time.time()-s))
        return True

    @api.multi
    def _compute_amount(self):
        self._cr.execute("""
            select asset_depre_batch_id, sum(debit) as amount
            from account_move_line
            where asset_depre_batch_id in %s
            group by asset_depre_batch_id
        """, (tuple(self.ids), ))
        amount_dict = dict([(x[0], x[1]) for x in self._cr.fetchall()])
        for rec in self:
            rec.amount = amount_dict.get(rec.id, 0.0)
        return True
