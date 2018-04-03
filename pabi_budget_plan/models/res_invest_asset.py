# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class ResInvestAsset(models.Model):
    _inherit = 'res.invest.asset'

    @api.multi
    def generate_code(self):
        """ Generate Asset Code based on context fiscalyear_id """
        Fiscal = self.env['account.fiscalyear']
        Seq = self.env['ir.sequence']
        fiscalyear_id = self._context.get('fiscalyear_id', False)
        for rec in self:
            if rec.code:
                continue
            if not fiscalyear_id:
                fiscalyear_id = rec.fiscalyear_id.id or Fiscal.find()
            ctx = {'fiscalyear_id': fiscalyear_id}
            rec.write({
                'fiscalyear_id': fiscalyear_id,
                'code': Seq.with_context(ctx).next_by_code('invest.asset'), })

    @api.model
    def _add_name_search_domain(self):
        """ only asset not being used in other budget control """
        domain = super(ResInvestAsset, self)._add_name_search_domain()
        if self._context.get('show_unused_invest_asset', False):
            fiscalyear_id = self._context.get('fiscalyear_id', False)
            asset_ids = self.env['account.budget.line'].search(
                [('chart_view', '=', 'invest_asset'),
                 ('fiscalyear_id', '=', fiscalyear_id)]
            ).mapped('invest_asset_id').ids
            domain += [('id', 'not in', asset_ids)]
        return domain
