# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref = fields.Char(index=True)
    narration = fields.Text(index=True)

    @api.model
    def create(self, vals):
        # Case stock picking with force journal_id
        if self._context.get('overwrite_journal_id', False):
            vals['journal_id'] = self._context['overwrite_journal_id']
        elif self._context.get('active_model', False) == 'stock.picking':
            if 'journal_id' in vals:
                picking_id = self._context.get('active_id', False)
                picking = self.env['stock.picking'].browse(picking_id)
                if picking.asset_journal_id:  # If asset, use asset journal
                    vals['journal_id'] = picking.asset_journal_id.id
        # Move name to '/'
        if self._context.get('overwrite_move_name', False):
            vals['name'] = '/'
        return super(AccountMove, self).create(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_id = fields.Many2one(
        'account.asset',
        index=True,  # Add index
    )
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
            # Buildings
            'building_id': move_line.stock_move_id.building_id.id,
            'floor_id': move_line.stock_move_id.floor_id.id,
            'room_id': move_line.stock_move_id.room_id.id,
            'responsible_user_id':
            move_line.stock_move_id.responsible_user_id.id,
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
    
    
    @api.multi
    def _check_account_move_line(self):
        if self.document_id:
            if self.chartfield_id:
                search_picking = self.env['stock.picking'].search([['id','=',self.document_id.id],['origin','like','POS']])
                if search_picking:
                    search = self.env['account.move.line'].search([['move_id','=',self.move_id.id]])
                    for rec in search:
                        if not rec.chartfield_id:
                            rec.costcenter_id = self.costcenter_id.id
                            rec.org_id = self.org_id.id
                            rec.fund_id = self.fund_id.id
                            rec.chartfield_id = self.chartfield_id.id
            else:
                search = self.env['account.move.line'].search([['move_id','=',self.move_id.id],
                                                               ['costcenter_id','!=',False],
                                                               ['org_id','!=',False]],limit=1)
                if search:
                    self.costcenter_id = search.costcenter_id.id
                    self.org_id = search.org_id.id
                    self.fund_id = search.fund_id.id
                    self.chartfield_id = search.chartfield_id.id
                    
        self._get_detail_chartfield_id()
    
    @api.model
    def create(self, vals):
        move_line = super(AccountMoveLine, self).create(vals)
        if move_line.asset_id and (move_line.asset_id.code or '/') == '/':
            if move_line.asset_profile_id and move_line.asset_id:
                vals = self._prepare_asset_vals(move_line)
                move_line.asset_id.write(vals)
                # Asset must have account_analytic_id, if not exists
                if not move_line.asset_id.account_analytic_id:
                    Analytic = self.env['account.analytic.account']
                    move_line.asset_id.account_analytic_id = \
                        Analytic.create_matched_analytic(move_line.asset_id)
                # --
        #if move_line.chartfield_id:
        move_line._check_account_move_line()
        return move_line
    
    @api.multi
    def write(self, vals):
        if vals.get('chartfield_id') and not vals.get('costcenter_id') and not vals.get('org_id'):
            search = self._get_record_chartfield(vals.get('chartfield_id'))
            if search:
                vals['costcenter_id'] = search.costcenter_id.id
                vals['org_id'] = search.org_id.id
                
        res = super(AccountMoveLine, self).write(vals)
        return res
        
    
