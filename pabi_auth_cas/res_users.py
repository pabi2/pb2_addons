# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenElanz
#    Copyright (C) 2012-2013 Elanz Centre (<http://www.openelanz.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import fields, osv
from openerp.exceptions import AccessDenied

import logging

_logger = logging.getLogger(__name__)


class res_users(osv.osv):
    _inherit = 'res.users'

    _columns = {
        'cas_key': fields.char('CAS Key', size=16, readonly=True),
    }

    def check_credentials(self, cr, uid, password):
        # We try to connect the user with his password by the standard way
        try:
            return super(res_users, self).check_credentials(cr, uid, password)
        # If it failed, we try to do it thanks to the cas key created by the
        # Controller
        except AccessDenied:
            if not password:
                raise AccessDenied()
            cr.execute("""SELECT COUNT(1)
                                FROM res_users
                               WHERE id=%s
                                 AND cas_key=%s""",
                       (int(uid), password))
            if not cr.fetchone()[0]:
                raise AccessDenied()
