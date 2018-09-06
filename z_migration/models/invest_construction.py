# -*- coding: utf-8 -*-
from openerp import models, api


class ResInvestConstruction(models.Model):
    _inherit = 'res.invest.construction'

    @api.multi
    def mork_action_submit(self):
        self.action_submit()
        return True

    @api.multi
    def mork_action_approve(self):
        self.action_approve()
        return True


class RestInvestConstructionPhase(models.Model):
    _inherit = 'res.invest.construction.phase'

    @api.multi
    def mork_action_submit(self):
        self.action_submit()
        return True

    @api.multi
    def mork_action_approve(self):
        self.action_approve()
        return True
