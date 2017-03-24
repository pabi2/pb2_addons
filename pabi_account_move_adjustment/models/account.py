# -*- coding: utf-8 -*-
from openerp import models, fields, api


MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountMove(models.Model):
    _inherit = 'account.move'

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
        # For case adjustment journal only, create analytic when posted
        for move in self:
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

    @api.multi
    def action_set_tax_sequence(self):
        for move in self:
            move.tax_detail_ids._set_next_sequence()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def create_analytic_lines(self):
        """ For balance sheet item, do not create analytic line """
        # Before create, always remove analytic line if exists
        for move_line in self:
            move_line.analytic_lines.unlink()
        move_lines = self.filtered(
            lambda l: l.journal_id.type != 'adjust_no_budget')
        return super(AccountMoveLine, move_lines).create_analytic_lines()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(
        selection_add=[('adjust_budget', 'Adjust Budget'),
                       ('adjust_no_budget', 'Adjust No-Budget')],
    )

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'adjust_no_budget':
            self.analytic_journal_id = False

    @api.multi
    def write(self, vals):
        if vals.get('type', False):
            if vals.get('type') == 'adjust_no_budget':
                vals['analytic_journal_id'] = False
        return super(AccountJournal, self).write(vals)
