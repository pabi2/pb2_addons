# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def create_internal_charge_move(self):
        """ When internal charge move is created, send signal = accepted """
        res = super(HRExpense, self).create_internal_charge_move()
        try:
            signals = {'accepted': '1', 'cancelled': '2'}
            for exp in self:
                exp.send_signal_to_pabiweb(signals['accepted'])
        except Exception, e:
            self._cr.rollback()
            raise ValidationError(str(e))
        return res
