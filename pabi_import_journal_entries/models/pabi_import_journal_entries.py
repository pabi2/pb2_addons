# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare
from openerp.addons.pabi_chartfield_merged.models.chartfield import \
    MergedChartField
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


@job
def action_done_async_process(session, model_name, res_id):
    try:
        res = session.pool[model_name].action_done_backgruond(
            session.cr, session.uid, [res_id], session.context)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)


class PabiImportJournalEntries(models.Model):
    _name = 'pabi.import.journal.entries'
    _order = 'name desc'
    _description = 'Import Journal Entries'

    name = fields.Char(
        string='Name',
        default='/',
        readonly=True,
        copy=False,
    )
    note = fields.Char(
        string='Note',
        size=500,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='State',
        default='draft',
        help="* Draft: first created, user preview\n"
        "* Done: all journal entries split\n"
        "* Cancelled: user choose to delete and will redo again"
    )
    line_ids = fields.One2many(
        'pabi.import.journal.entries.line',
        'import_id',
        string='Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True,
    )
    move_count = fields.Integer(
        string='JE Count',
        compute='_compute_moves',
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Entries',
        readonly=True,
        copy=False,
    )
    commit_every = fields.Integer(
        default=100,
    )

    split_entries_job_id = fields.Many2one(
        'queue.job',
        string='split entries Job',
        compute='_compute_split_entries_job_uuid',
    )
    split_entries_uuid = fields.Char(
        string='split entries Job UUID',
        compute='_compute_split_entries_job_uuid',
    )
###########################--------------------------------- start job backgruond ------------------------------- #######################
    @api.multi
    def _compute_split_entries_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_done_async_process', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.split_entries_job_id = jobs and jobs[0] or False
            rec.split_entries_uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def action_done(self):
        for rec in self:
            rec.split_entries()
        return True

    @api.multi
    def action_done_backgruond(self):
        if self._context.get('split_entries_async_process', False):
            self.ensure_one()
            if self._context.get('job_uuid', False):  # Called from @job
                return self.action_done()
            if self.split_entries_job_id:
                message = _('Confirm Split Entries')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Confirm Split Entries' % self.name
            uuid = action_done_async_process.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            #job.process_id = self.env.ref('pabi_async_process.'
            #                              'confirm_pos_order')
        else:
            return self.action_done()

###########################--------------------------------- end job backgruond ------------------------------- #######################




    @api.multi
    def _compute_moves(self):
        for rec in self:
            rec.move_count = len(rec.move_ids)
        return True

    @api.multi
    def open_entries(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update({'default_doctype': 'adjustment',
                    'direct_create': True})
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
            'nodestroy': True,
            'domain': [('id', 'in', self.move_ids.ids)],
        }

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('pabi.import.journal.entries') or '/'
        return super(PabiImportJournalEntries, self).create(vals)

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def split_entries(self):
        """ For each repat Ref, do create journal entries
            and commit every 100 record """
        self.ensure_one()
        # do first time only
        if not self._context.get('not_unlink', False) and \
                not any(self.line_ids.mapped('check_commit')):
            self.move_ids.unlink()
        moves = {}
        for line in self.line_ids:
            if not moves.get(line.ref, False):
                moves[line.ref] = []
            vals = {
                'ref': line.ref,
                'journal_id': line.journal_id.id,
                'date': line.date,
                'to_be_reversed': line.to_be_reversed,
                'docline_seq': line.docline_seq,
                'partner_id': line.partner_id.id,
                'activity_group_id': line.activity_group_id.id,
                'activity_id': line.activity_id.id,
                'account_id': line.account_id.id,
                'name': line.name,
                'debit': line.debit,
                'credit': line.credit,
                'chartfield_id': line.chartfield_id.id,
                'cost_control_id': line.cost_control_id.id,
                'origin_ref': line.origin_ref,
                # More data
                'period_id': self.env['account.period'].find(line.date).id,
                'fund_id': line.fund_id or line._get_default_fund(),
            }
            moves[line.ref].append(vals)
        # first time to create all move
        if not self._context.get('not_unlink', False) and \
                not any(self.line_ids.mapped('check_commit')):
            for ref, lines in moves.iteritems():
                move_dict = {'ref': ref}
                for l in lines:
                    period_id = \
                        self.env['account.period'].find(dt=line['date']).id
                    move_dict.update({
                        'journal_id': l['journal_id'],
                        'date': l['date'],
                        'to_be_reversed': l['to_be_reversed'],
                        'period_id': period_id,
                    })
                new_move = self.env['account.move'].create(move_dict)
                new_move.date_document = new_move.date  # Reset date
                self.move_ids += new_move
        # Search line depend on commit
        lines = self.env['pabi.import.journal.entries.line'].search([
            ('import_id', '=', self.id),
            ('check_commit', '=', False)], limit=self.commit_every)
        if lines:
            # Create JE
            move_lines = []
            for l in lines:
                period_id = \
                    self.env['account.period'].find(dt=line['date']).id
                move_lines.append((0, 0, {
                    'ref': l.ref,
                    'docline_seq': l.docline_seq,
                    'partner_id': l.partner_id.id,
                    'activity_group_id': l.activity_group_id.id,
                    'activity_id': l.activity_id.id,
                    'account_id': l.account_id.id,
                    'name': l.name,
                    'debit': l.debit,
                    'credit': l.credit,
                    'chartfield_id': l.chartfield_id.id,
                    'cost_control_id': l.cost_control_id.id,
                    'origin_ref': l.origin_ref,
                    # More data
                    'period_id': period_id,
                    'fund_id': line._get_default_fund(),
                    }))
            lines.write({'check_commit': True})
            move_line = []
            for move_id in self.move_ids:
                for ml in move_lines:
                    if ml[2].get('ref') == move_id.ref:
                        move_line.append(ml)
                move_id.write({'line_id': move_line})
                move_line = []
            self.env.cr.commit()
            print("=============if====================")
            return self.with_context({'not_unlink': True}).split_entries()
        else:
            self.write({'state': 'done'})
            # self._validate_new_move(new_move)
            return True

    @api.model
    def _validate_new_move(self, move):
        ag_lines = move.line_id.filtered('activity_group_id')
        # JV must have AG/A
        if move.journal_id.analytic_journal_id and not ag_lines:
            raise ValidationError(
                _('For JV (Adjust Budget), %s'
                  'at least 1 line must have AG/A!') % move.ref)
        # JN must not have AG/A
        if not move.journal_id.analytic_journal_id and ag_lines:
            raise ValidationError(
                _('For JN (Adjust.No.Budget), %s'
                  'no line can have activity group!') % move.ref)
        # Debit != Credit
        if float_compare(sum(move.line_id.mapped('debit')),
                         sum(move.line_id.mapped('credit')), 2) != 0:
            raise ValidationError(_('Entry not balance %s!') % move.ref)


class PabiImportJournalEntriesLine(MergedChartField, models.Model):
    _name = 'pabi.import.journal.entries.line'
    _order = 'ref, docline_seq'

    import_id = fields.Many2one(
        'pabi.import.journal.entries',
        string='Import ID',
        index=True,
        ondelete='cascade',
    )
    check_commit = fields.Boolean(
        copy=False,
    )
    # Header
    ref = fields.Char(
        string='Reference',
        size=100,
        required=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('code', 'in', ('AJB', 'AJN'))],
        required=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
    )
    to_be_reversed = fields.Boolean(
        string='To Be Reversed',
        default=False,
    )
    # Lines
    docline_seq = fields.Integer(
        string='Sequence',
        default=0,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
    )
    name = fields.Char(
        string='Description',
        size=500,
    )
    debit = fields.Float(
        string='Debit',
        default=0.0,
    )
    credit = fields.Float(
        string='Credit',
        default=0.0,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
    )
    origin_ref = fields.Char(
        string='Document Ref.',
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        domain=[],  # Remove domain
    )
