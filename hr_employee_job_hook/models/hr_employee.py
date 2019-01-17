# -*- coding: utf-8 -*-
import logging

from openerp import models, api


_logger = logging.getLogger(__name__)

class HREmployeeJobHook(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def action_hook_profile(self, emps=[]):
        users = False
        if emps:
            users = self.search([
                ['active','=',True],
                ['sinid','!=', False],
                ['employee_code','in', emps]
            ])
        else:
            users = self.search([
                ['active','=',True],
                ['sinid','!=', False]
            ])
        for user in users:
            user.write({'section_id': user.section_id.id, 'sinid': False})
            if user.employee_code:
                _logger.info("Job Hook Profile PASS '%s'.", user.employee_code)
        return True

