# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class ResInvestAsset(models.Model):
    _inherit = 'res.invest.asset'

    @api.model
    def create(self, vals):
        # For asset code on create
        if not vals.get('fiscalyear_id', False):
            raise ValidationError(_('No fiscalyear for this invest asset!'))
        ctx = {'fiscalyear_id': vals['fiscalyear_id']}
        Seq = self.env['ir.sequence']
        vals['code'] = Seq.with_context(ctx).next_by_code('invest.asset')
        return super(ResInvestAsset, self).create(vals)
