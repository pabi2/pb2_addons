# -*- coding: utf-8 -*-
from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def fix_user_ou(self, user_logins=[]):
        if user_logins:
            _logger.info('Update OU for user_logins: %s' % user_logins)
        else:
            _logger.info('Update OU for all users in system.')
        """ Recompute OU for users (all if user not specified) """
        domain = []
        if user_logins:
            self._cr.execute("""
                select id from res_users where login in %s
            """, (tuple(user_logins), ))
            user_ids = [x[0] for x in self._cr.fetchall()]
            domain.append(('id', 'in', user_ids))
        users = self.search(domain)
        for user in users:
            user._compute_operating_unit()
            _logger.info('Updated OU for user: %s' % user.login)
        return True
