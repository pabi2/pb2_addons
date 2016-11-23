# -*- coding: utf-8 -*-
from openerp import models, api


class ResSection(models.Model):
    _inherit = 'res.section'

    @api.multi
    def name_get(self):
        if self._context.get('type') in ('in_invoice', 'in_refund',
                                         'out_invoice', 'out_invoice'):
            result = []
            for rec in self:
                result.append((rec.id, rec.code))
            return result
        else:
            return super(ResSection, self).name_get()


class ResProject(models.Model):
    _inherit = 'res.project'

    @api.multi
    def name_get(self):
        if self._context.get('type') in ('in_invoice', 'in_refund',
                                         'out_invoice', 'out_invoice'):
            result = []
            for rec in self:
                result.append((rec.id, rec.code))
            return result
        else:
            return super(ResProject, self).name_get()


class ResInvestAsset(models.Model):
    _inherit = 'res.invest.asset'

    @api.multi
    def name_get(self):
        if self._context.get('type') in ('in_invoice', 'in_refund',
                                         'out_invoice', 'out_invoice'):
            result = []
            for rec in self:
                result.append((rec.id, rec.code))
            return result
        else:
            return super(ResInvestAsset, self).name_get()
