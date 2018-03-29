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
