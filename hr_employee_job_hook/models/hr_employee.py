# -*- coding: utf-8 -*-
import logging

from openerp import models, api


_logger = logging.getLogger(__name__)

class HREmployeeJobHook(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def action_hook_profile(self):
        users = self.search([['active','=',True]])
        for user in users:
            user.write({'active': True})
            if user.employee_code:
                _logger.info("Job Hook Profile PASS '%s'.", user.employee_code)
        return True

