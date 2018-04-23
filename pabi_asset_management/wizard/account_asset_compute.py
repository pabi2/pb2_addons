# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _


class AccountAssetCompute(models.Model):  # Change to a Model
    _inherit = 'account.asset.compute'
    _rec_name = 'id'
    _order = 'id desc'

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    period_id = fields.Many2one(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        readonly=True,
        default='draft',
    )
    move_ids = fields.Many2many(
        'account.move',
        'asset_compute_account_move_rel',
        'compute_id', 'move_id',
        string='Journal Entries',
        readonly=True,
    )

    @api.multi
    def asset_compute(self):
        res = super(AccountAssetCompute, self).asset_compute()
        domain = ast.literal_eval(res['domain'])
        move_ids = domain[0][2]
        self.write({'move_ids': [(6, 0, move_ids)],
                    'state': 'done'})
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
            'domain': [('id', 'in', self.move_ids.ids)],
        }
