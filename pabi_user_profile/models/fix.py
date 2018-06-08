# -*- coding: utf-8 -*-
from openerp import models, api


class ResUser(models.Model):
    _inherit = 'res.user'

    @api.model
    def fix_user_ou(self):
        """ Auto recompute OU for all users (if not exists) """
        users = self.search([])
        users._compute_operating_unit()
