# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True,
        help="When account is created by a stock move (anglo saxon).",
    )
    parent_asset_id = fields.Many2one(
        'account.asset',
        string='Parent Asset',
        readonly=True,
        help="If in purchase order line, parent asset is specified.",
    )

    @api.model
    def _prepare_asset_vals(self, move_line):
        sequence = move_line.product_id.sequence_id
        if not sequence:
            raise ValidationError(_('No asset sequence setup!'))
        code = self.env['ir.sequence'].next_by_id(sequence.id)
        vals = {
            'product_id': move_line.product_id.id,
            'move_id': move_line.stock_move_id.id,
            'asset_purchase_method_id':
            # Case direct receive, chosen by user in stock.picking
            move_line.stock_move_id.picking_id.asset_purchase_method_id.id or
            # Case Asset Transfer, inherit from source asset
            self._context.get('asset_purchase_method_id', False) or
            # Normal case, start from PR, link back to original document
            move_line.stock_move_id.purchase_line_id.quo_line_id.
            requisition_line_id.requisition_id.purchase_method_id.
            asset_purchase_method_id.id,
            'parent_id': move_line.parent_asset_id.id,
            'code': code,
            # Budget Source, from 4 structure
            'section_id': move_line.section_id.id,
            'project_id': move_line.project_id.id,
            'invest_asset_id': move_line.invest_asset_id.id,
            'invest_construction_phase_id':
            move_line.invest_construction_phase_id.id,
            # Owner
            # - project -> project
            # - section -> section
            # - invest_asset, invest_construction_phase -> section
            'owner_section_id': move_line.section_id.id or
            move_line.invest_construction_id.pm_section_id.id or
            move_line.invest_asset_id.owner_section_id.id,
            'owner_project_id': move_line.project_id.id,
        }
        # With context data about the installment
        if self._context.get('work_acceptance_id', False):
            installment = self._context.get('installment', False)
            num_installment = self._context.get('num_installment', False)
            vals.update({'installment': installment,
                         'num_installment': num_installment,
                         })
        # --
        if not (vals['section_id'] or vals['project_id'] or
                vals['invest_asset_id'] or
                vals['invest_construction_phase_id']):
            raise ValidationError(
                _('Source of budget is not specified!'))
        if not (vals['owner_section_id'] or vals['owner_project_id']):
            raise ValidationError(
                _('Project/Section owner of asset not specified!'))
        return vals

    @api.model
    def create(self, vals):
        move_line = super(AccountMoveLine, self).create(vals)
        if move_line.asset_id and (move_line.asset_id.code or '/') == '/':
            if move_line.asset_profile_id and move_line.asset_id:
                vals = self._prepare_asset_vals(move_line)
                move_line.asset_id.write(vals)
        return move_line

    # @api.multi
    # def _budget_eligible_move_lines(self):
    #   move_lines = super(AccountMoveLine, self)._budget_eligible_move_lines()
    #     # Add move line with fixed asset account
    #     move_lines += self.filtered(
    #         lambda l: l.account_id.user_type.for_asset and
    #         (l.activity_id or l.product_id)  # Is Activity or Product
    #     )
    #     return move_lines
