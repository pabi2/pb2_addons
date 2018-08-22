# -*- coding: utf-8 -*-
from openerp import models, api


class AutoApproveInvestConstruction(models.Model):
    _name = 'auto.approve.invest.construction'

    @api.multi
    def confirm_approve(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        InvestConstruction = self.env['res.invest.construction']
        invest_construction_ids = []
        for rec in InvestConstruction.browse(active_ids):
            try:
                if rec.state != 'draft':
                    continue
                # Submit
                rec.action_submit()
                # Approve
                rec.action_approve()
            except Exception:
                invest_construction_ids.append(rec.id)

        # Return project as not pass
        action = self.env.ref('pabi_invest_construction.'
                              'action_invest_construction')
        result = action.read()[0]
        result.update({
            'domain': [('id', 'in', invest_construction_ids)]
        })
        if not invest_construction_ids:
            result = True
        return result
