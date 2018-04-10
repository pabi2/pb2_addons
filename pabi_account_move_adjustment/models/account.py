# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.addons.pabi_chartfield_merged.models.chartfield \
    import MergedChartField
from openerp.exceptions import ValidationError


MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']

    state = fields.Selection(track_visibility='always')
    name = fields.Char(track_visibility='onchange')
    ref = fields.Char(track_visibility='onchange')
    journal_id = fields.Many2one('account.journal',
                                 track_visibility='onchange')
    period_id = fields.Many2one('account.period',
                                track_visibility='onchange')
    to_be_reversed = fields.Boolean(track_visibility='onchange')
    to_check = fields.Boolean(track_visibility='onchange')
    line_id = fields.One2many('account.move.line',
                              track_visibility='onchange')
    narration = fields.Text(track_visibility='onchange')
    due_history_ids = fields.One2many(
        'account.move.due.history',
        'move_id',
        string='Due History',
        readonly=True,
    )
    date_due = fields.Date(
        string='Due Date',
        compute='_compute_date_due',
        readonly=True,
    )

    @api.multi
    def _compute_date_due(self):
        for rec in self:
            date_due = rec.line_id.mapped('date_maturity')
            if date_due:
                rec.date_due = date_due[0]
            else:
                rec.date_due = False

    @api.multi
    def reset_desc(self):
        for rec in self:
            rec.narration = rec.line_item_summary
        return True

    @api.multi
    def action_set_tax_sequence(self):
        for rec in self:
            rec.tax_detail_ids._compute_taxbranch_id()
        return super(AccountMove, self).action_set_tax_sequence()

    @api.one
    def copy(self, default):
        move = super(AccountMove, self).copy(default)
        if self.doctype == 'adjustment':
            move.line_id.write({'analytic_account_id': False})
            self.env['account.analytic.line'].search(
                [('move_id', 'in', move.line_id.ids)]).unlink()
        return move

    @api.model
    def _convert_move_line_to_dict(self, line):
        values = {}
        for name, field in line._fields.iteritems():
            if name in MAGIC_COLUMNS:
                continue
            elif field.type == 'many2one':
                values[name] = line[name].id
            elif field.type not in ['many2many', 'one2many']:
                values[name] = line[name]
        return values

    @api.multi
    def button_validate(self):
        for move in self:
            if move.date < move.period_id.date_start or \
                    move.date > move.period_id.date_stop:
                raise ValidationError(_('Period conflict with date!'))
            # Validate for tax detail
            if True in move.line_id.mapped('is_tax_line') \
                    and not move.tax_detail_ids:
                raise ValidationError(_('Please fill Tax Detail!'))
            # Validate Adjustment Doctype, at lease 1 line must have AG/A
            if self._context.get('default_doctype', False) == 'adjustment':
                ag_lines = move.line_id.filtered('activity_group_id')
                # JV must have AG/A
                if move.journal_id.analytic_journal_id and not ag_lines:
                    raise ValidationError(
                        _('For budget related transaction, '
                          'at least 1 line must have AG/A!'))
                # JN must not have AG/A
                if not move.journal_id.analytic_journal_id and ag_lines:
                    raise ValidationError(
                        _('For JN, No line can have activity gorup!'))
            # For case adjustment journal only, create analytic when posted
            Analytic = self.env['account.analytic.account']
            # Only direct creation of account move, we will recompute dimension
            if self._context.get('direct_create', False) and \
                    move.doctype == 'adjustment':
                # if move.doctype == 'adjustment':
                # Analytic
                for line in move.line_id:
                    vals = self._convert_move_line_to_dict(line)
                    line.update_related_dimension(vals)
                    analytic = Analytic.create_matched_analytic(line)
                    line.analytic_account_id = analytic
        return super(AccountMove, self).button_validate()

    @api.multi
    def button_cancel(self):
        # For case adjustment journal only, remove analytic when cancel
        for move in self:
            if move.doctype == 'adjustment':
                move.line_id.write({'analytic_account_id': False})
                self.env['account.analytic.line'].search(
                    [('move_id', 'in', move.line_id.ids)]).unlink()
        return super(AccountMove, self).button_cancel()

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        invoice_id = self._context.get('src_invoice_id', False)
        if invoice_id:
            Invoice = self.env['account.invoice']
            invoice = Invoice.browse(invoice_id)
            invoice.write({'adjust_move_id': move.id})
        return move


class AccountMoveLine(MergedChartField, models.Model):
    _inherit = 'account.move.line'

    is_tax_line = fields.Boolean(
        string='Is Tax Line',
        help="Flag to mark this line as require tax detial on adjustment",
    )

    @api.multi
    @api.onchange('account_id')
    def _onchange(self):
        self.is_tax_line = False
        self.tax_code_id = False
        if self.account_id:
            taxes = self.env['account.tax'].search([
                ('account_collected_id', '=', self.account_id.id)])
            if taxes:
                tax_code = taxes[0].mapped('tax_code_id')
                self.tax_code_id = tax_code
                due_tax = taxes.filtered(lambda l: (l.is_undue_tax is False and
                                                    l.is_wht is False))
                self.is_tax_line = due_tax and True or False

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self._context.get('default_doctype', False) == 'adjustment':
            self.account_id = self.activity_id.account_id

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        if self._context.get('default_doctype', False) == 'adjustment':
            self.activity_id = False

    @api.onchange('chartfield_id')
    def _onchange_chartfield_id(self):
        if self._context.get('default_doctype', False) == 'adjustment':
            self.fund_id = False
            # display costcenter only if avail.
            if 'costcenter_id' in self and self.chartfield_id.costcenter_id:
                self.costcenter_id = self.chartfield_id.costcenter_id
            # Change other chartfield, we need it to set domain on Fund
            res_id = self.chartfield_id.res_id
            if self.chartfield_id.model == 'res.section':
                self.section_id = res_id
            if self.chartfield_id.model == 'res.project':
                self.project_id = res_id
            if self.chartfield_id.model == 'res.invest.construction.phase':
                self.invest_construction_phase_id = res_id
            if self.chartfield_id.model == 'res.invest.asset':
                self.invest_asset_id = res_id
            if self.chartfield_id.model == 'res.project':
                self.project_id = res_id

    @api.multi
    @api.constrains('activity_group_id', 'activity_id')
    def _check_activity_group(self):
        for rec in self:
            if rec.activity_group_id and \
                    not (rec.activity_id or rec.activity_rpt_id):
                raise ValidationError(
                    _('Actvitiy is required for activity group!'))

    # @api.multi
    # def create_analytic_lines(self):
    #     """ For balance sheet item, do not create analytic line """
    #     # Before create, always remove analytic line if exists
    #     for move_line in self:
    #         move_line.analytic_lines.unlink()
    #     # Only create analytic line if adjust for budget
    #     move_lines = self.filtered(
    #         lambda l: l.journal_id.type != 'adjust_no_budget')
    #     return super(AccountMoveLine, move_lines).create_analytic_lines()


# class AccountJournal(models.Model):
#     _inherit = 'account.journal'
#
#     type = fields.Selection(
#         selection_add=[('adjust_budget', 'Adjust Budget'),
#                        ('adjust_no_budget', 'Adjust No-Budget')],
#     )
#
#     @api.onchange('type')
#     def _onchange_type(self):
#         if self.type == 'adjust_no_budget':
#             self.analytic_journal_id = False
#
#     @api.multi
#     def write(self, vals):
#         if vals.get('type', False):
#             if vals.get('type') == 'adjust_no_budget':
#                 vals['analytic_journal_id'] = False
#         return super(AccountJournal, self).write(vals)


class AccountModel(models.Model):
    _inherit = 'account.model'

    journal_id = fields.Many2one(
        'account.journal',
        domain=[('code', 'in', ('AJB', 'AJN'))],
        help="In PABI2, only 2 type of journal is allowed for adjustment",
    )

    # If AJN (Not adjust budget), user must not choose any budget.
    # @api.multi
    # @api.constrains('lines_id', 'journal_id')
    # def _check_adjust_no_budget(self):
    #     for rec in self:
    #         if rec.journal_id.code == 'AJN' and \
    #                 rec.lines_id.filtered('chartfield_id'):
    #             raise ValidationError(_('For %s, budget are not allowed') %
    #                                   rec.journal_id.name)

    @api.multi
    def onchange_journal_id(self, journal_id):
        res = super(AccountModel, self).onchange_journal_id(journal_id)
        res['value']['lines_id'] = False
        return res


class AccountModelLine(models.Model):
    _inherit = 'account.model.line'

    budget_journal = fields.Boolean(
        string='Budget Journal',
        compute='_compute_budget_journal',
    )

    @api.onchange('budget_journal')
    def _onchange_budget_journal(self):
        analytic_journal = self.model_id.journal_id.analytic_journal_id
        self.budget_journal = analytic_journal and True or False

    @api.multi
    def _compute_budget_journal(self):
        for rec in self:
            analytic_journal = rec.model_id.journal_id.analytic_journal_id
            rec.budget_journal = analytic_journal and True or False


class AccountModelType(models.Model):
    _inherit = 'account.model.type'

    journal_id = fields.Many2one(
        'account.journal',
        domain=[('code', 'in', ('AJB', 'AJN'))],
        help="In PABI2, only 2 type of journal is allowed for adjustment",
    )


class AccountMoveDueHistory(models.Model):
    _name = 'account.move.due.history'
    _order = 'write_date desc'

    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        ondelete='cascade',
        index=True,
    )
    date_old_due = fields.Date(
        string='Old Due Date',
        readonly=True,
    )
    date_due = fields.Date(
        string='New Due Date',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Updated By',
        readonly=True,
    )
    write_date = fields.Datetime(
        string='Updated Date',
        readonly=True,
    )
    reason = fields.Char(
        string='Reason',
    )
