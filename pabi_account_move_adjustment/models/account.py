# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.addons.pabi_chartfield_merged.models.chartfield \
    import MergedChartField
from openerp.exceptions import ValidationError


MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountMove(models.Model):
    _inherit = 'account.move'

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
            # Validate for tax detail
            if True in move.line_id.mapped('is_tax_line') \
                    and not move.tax_detail_ids:
                raise ValidationError(_('Please fill Tax Detail!'))
            # For case adjustment journal only, create analytic when posted
            Analytic = self.env['account.analytic.account']
            if move.doctype == 'adjustment':
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
    @api.multi
    @api.constrains('lines_id', 'journal_id')
    def _check_adjust_no_budget(self):
        for rec in self:
            if rec.journal_id.code == 'AJN' and \
                    rec.lines_id.filtered('chartfield_id'):
                raise ValidationError(_('For %s, budget are not allowed') %
                                      rec.journal_id.name)
