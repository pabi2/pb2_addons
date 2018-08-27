# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAssetAdjust(models.Model):
    _inherit = 'account.asset.adjust'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'asset_adjust'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        # It will try to use doctype_id first, if not available, rollback
        name = self.env['ir.sequence'].get('account.asset.adjust')
        vals.update({'name': name})
        return super(AccountAssetAdjust, self).create(vals)


class AccountAssetAdjustLine(models.Model):
    _inherit = 'account.asset.adjust.line'

    @api.multi
    def write(self, vals):
        res = super(AccountAssetAdjustLine, self).write(vals)
        if vals.get('cancel_move_id', False):
            for adjust in self:
                # get doctype
                refer_type = 'asset_adjust'
                doctype = self.env['res.doctype'].get_doctype(refer_type)
                # --
                if doctype.reversal_sequence_id:
                    sequence_id = doctype.reversal_sequence_id.id
                    fy_id = adjust.cancel_move_id.period_id.fiscalyear_id.id
                    adjust.cancel_move_id.write({
                        'name': self.with_context({'fiscalyear_id': fy_id}).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res


class AccountAssetAdjustExpenseToAsset(models.Model):
    _inherit = 'account.asset.adjust.expense_to_asset'

    @api.multi
    def write(self, vals):
        res = super(AccountAssetAdjustExpenseToAsset, self).write(vals)
        if vals.get('cancel_move_id', False):
            for adjust in self:
                # get doctype
                refer_type = 'asset_adjust'
                doctype = self.env['res.doctype'].get_doctype(refer_type)
                # --
                if doctype.reversal_sequence_id:
                    sequence_id = doctype.reversal_sequence_id.id
                    fy_id = adjust.cancel_move_id.period_id.fiscalyear_id.id
                    adjust.cancel_move_id.write({
                        'name': self.with_context({'fiscalyear_id': fy_id}).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res


class AccountAssetAdjustAssetToExpense(models.Model):
    _inherit = 'account.asset.adjust.asset_to_expense'

    @api.multi
    def write(self, vals):
        res = super(AccountAssetAdjustAssetToExpense, self).write(vals)
        if vals.get('cancel_move_id', False):
            for adjust in self:
                # get doctype
                refer_type = 'asset_adjust'
                doctype = self.env['res.doctype'].get_doctype(refer_type)
                # --
                if doctype.reversal_sequence_id:
                    sequence_id = doctype.reversal_sequence_id.id
                    fy_id = adjust.cancel_move_id.period_id.fiscalyear_id.id
                    adjust.cancel_move_id.write({
                        'name': self.with_context({'fiscalyear_id': fy_id}).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res
