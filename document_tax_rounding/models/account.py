# -*- coding: utf-8 -*-
from openerp import models, api


class account_tax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _get_tax_calculation_rounding_method(self, taxes):
        res = super(account_tax, self).\
              _get_tax_calculation_rounding_method(taxes)
        if taxes and self._context.get('method'):
            res = self._context.get('method')
            return res
        else:
            return False
