
from openerp import models, fields, api, _


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

    @api.multi
    def _compute_moves(self):
        Move = self.env['account.move']
        for rec in self:
            rec.move_count = \
                Move.search_count([('asset_depre_batch_id', '=', rec.id)])
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
    def post_entries(self):
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
