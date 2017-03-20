# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import ChartField

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
