# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare
from openerp.addons.pabi_chartfield_merged.models.chartfield import \
    MergedChartField


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
        """ For each repat Ref, do create journal entries """
        self.ensure_one()
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
        # Create JE
        for ref, lines in moves.iteritems():
            move_dict = {'ref': ref}
            move_lines = []
            i = 0
            for l in lines:
                period_id = self.env['account.period'].find(dt=line['date']).id
                if i == 0:  # First loop
                    move_dict.update({
                        'journal_id': l['journal_id'],
                        'date': l['date'],
                        'to_be_reversed': l['to_be_reversed'],
                        'period_id': period_id,
                    })
                i += 1
                move_lines.append((0, 0, {
                    'docline_seq': l['docline_seq'],
                    'partner_id': l['partner_id'],
                    'activity_group_id': l['activity_group_id'],
                    'activity_id': l['activity_id'],
                    'account_id': l['account_id'],
                    'name': l['name'],
                    'debit': l['debit'],
                    'credit': l['credit'],
                    'chartfield_id': l['chartfield_id'],
                    'cost_control_id': l['cost_control_id'],
                    'origin_ref': l['origin_ref'],
                    # More data
                    'period_id': period_id,
                    'fund_id': line._get_default_fund(),
                    }))
            move_dict['line_id'] = move_lines
            new_move = self.env['account.move'].create(move_dict)
            new_move.date_document = new_move.date  # Reset date
            self._validate_new_move(new_move)
            self.move_ids += new_move
        self.write({'state': 'done'})
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
