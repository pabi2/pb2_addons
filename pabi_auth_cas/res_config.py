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
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _

from .pycas import login

default_host = 'http://127.0.0.1:8069/'
# default_port = 8443
default_service = ''


class cas_base_config_settings(osv.TransientModel):

    _inherit = 'base.config.settings'
    _columns = {
        'cas_activated': fields.boolean('CAS authentication activated',
                                        help='The CAS authentication only'
                                        ' works if you are in a single'
                                        ' You can launch the'
                                        'OpenERP Server with the option'
                                        ' database mode.'
                                        '--db-filter=YOUR_DATABASE to do so.'),
        'cas_server': fields.char('CAS Server address', required=True),
        'cas_service': fields.char('CAS Server service', required=True),
        #         'cas_server_port': fields.integer('CAS Server port'),
        'cas_create_user': fields.boolean('Users created on the fly',
                                          help='Automatically create local'
                                          ' user accounts for new users'
                                          ' authenticating  via CAS'),
    }

    default = {
        'create_user': False,
    }

    def get_default_cas_values(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'cas_activated': safe_eval(
                icp.get_param(cr,
                              uid,
                              'cas_auth.cas_activated',
                              'False')),
            'cas_server': icp.get_param(cr,
                                        uid,
                                        'cas_auth.cas_server',
                                        default_host),
            'cas_service': icp.get_param(cr,
                                         uid,
                                         'cas_auth.cas_service',
                                         default_service),
            'cas_create_user': safe_eval(
                icp.get_param(cr,
                              uid,
                              'cas_auth.cas_create_user',
                              'True')),
        }

    # Setter is required too
    def set_cas_values(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')

        error = True

        # If the host OR the port is valid
#         if config.cas_server or config.cas_server_port:
        if config.cas_server:
            # If the host AND the port are valid, we can activate CAS
            # authentication and save all values
            if config.cas_server:
                if config.cas_activated:
                    icp.set_param(
                        cr,
                        uid,
                        'cas_auth.cas_activated',
                        str(config.cas_activated))
                    # There is no error
                    error = False
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server', config.cas_server)
                icp.set_param(
                    cr, uid, 'cas_auth.cas_service', config.cas_service)
            # Else, there is one error
            # If the host field is valid, we save it and the default port value
            elif config.cas_server:
                icp.set_param(
                    cr, uid, 'cas_auth.cas_server', config.cas_server)
                icp.set_param(
                    cr, uid, 'cas_auth.cas_service', config.cas_service)
            # Else, the host field is empty, but not the port field: we save it
            # and the default host value
            else:
                icp.set_param(cr, uid, 'cas_auth.cas_server', default_host)
                icp.set_param(
                    cr, uid, 'cas_auth.cas_service', config.cas_service)
        # If error is True, there is at least one error, so we deactivate CAS
        # authentication
        if error:
            icp.set_param(cr, uid, 'cas_auth.cas_activated', 'False')
            # If the host field is empty, we save his default value
            if not config.cas_server:
                icp.set_param(cr, uid, 'cas_auth.cas_server', default_host)
                icp.set_param(cr, uid, 'cas_auth.cas_service', default_service)

        # We save the field used to know if users have to be created on the fly
        # or not
        icp.set_param(
            cr, uid, 'cas_auth.cas_create_user', str(config.cas_create_user))

    def check_cas_server(self, cr, uid, ids, context=None):
        """ Check if CAS paramaters (host and port) are valids """
        title = 'cas_check_fail'
        message = 'Bad parameters\n'
        message += 'There seems to be an error in the configuration.'
        config = self.browse(cr, uid, ids[0], context=context)
        cas_server = config.cas_server
        cas_service = config.cas_service
        try:
            res = login(cas_server, cas_service, ' ')
            if res[0] == 3:
                title = 'cas_check_success'
                message = 'Good parameters\n'
                message += 'The CAS server is well configured !'

        except:
            pass

        raise osv.except_osv(_(title), _(message))
