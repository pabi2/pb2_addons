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

# import cgi
import logging
# import os
# import tempfile
# import getpass
import urllib
# import urllib2
# import urlparse  -> Suplicated
import werkzeug
import werkzeug.utils
import werkzeug.urls
import werkzeug.exceptions
# import time
# import Cookie
# import operator
import ssl

from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs

# from openid import oidutil
# from openid.store import filestore
# from openid.consumer import consumer
from openid.cryptutil import randomString
# from openid.extensions import ax, sreg

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler
from openerp.modules.registry import RegistryManager
from openerp.addons.web.controllers.main import login_and_redirect
# set_cookie_and_redirect
import openerp.http as http
from openerp.http import request
from openerp.tools.translate import _

from ..pycas import login
# from ..pycas import make_pycas_cookie
from openerp.addons.web.controllers import main
from openerp.addons.web.controllers.main import Session

_logger = logging.getLogger(__name__)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def page_access_denied(app=''):
    url = 'https://i.nstda.or.th'
    message1 = _('You do not have permission to access this page ' + app + '.')
    message2 = _('Please contact your system administrator or')
    message_return_page = _('Go to Home')
    return """<html>
                <head>
                    <meta http-equiv="refresh" content="3; url=%s" />
                    <title>403 Forbidden</title>
                    <script></script>
                </head>
                <body>
                    <h1>HTTP Status 403 - Access is denied</h1><br/>
                    <h3>%s</h3>
                    <h3>%s <a href="%s">%s</a></h3>
                </body>
            </html>""" % (url, message1, message2, url, message_return_page)


def login_redirect_app():
    url = '/auth_cas?'
    if request.debug:
        url += 'debug&'
    return """<html><head><script>
        window.location = '%sapp=' + encodeURIComponent(window.location);
    </script></head></html>
    """ % (url,)


def login_redirect_cas(url, ticket):
    url_cas = '/auth_cas?ticket=' + ticket
    if request.debug:
        url += 'debug&'
    return """<html><head><script>
        window.location = '%s&app=' + encodeURIComponent('%s');
    </script></head></html>
    """ % (url_cas, url)


def get_base_url():
    dbname = getattr(request.session, 'db', False)
    config = CasController().get_config(dbname)
    url = ''
    if config['cas_service']:
        url = config['cas_service'][:-1]
    return url


class Session(openerp.addons.web.controllers.main.Session):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/adminlogin'):
        request.session.logout(keep_db=True)
#         Session().logout()
#         return werkzeug.utils.redirect(redirect, 303)
        return werkzeug.utils.redirect('https://i.nstda.or.th', 303)


class CasController(openerp.addons.web.controllers.main.Home):

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        return http.local_redirect(get_base_url() + '/auth_cas',
                                   query=request.params, keep_hash=True)

    @http.route('/web', type='http', auth="user")
    def web_client(self, s_action=None, menu=None, **kw):
        main.ensure_db()

        if request.session.uid:
            if kw.get('redirect'):
                return werkzeug.utils.redirect(kw.get('redirect'), 303)
            if not request.uid:
                request.uid = request.session.uid

        else:
            #             return login_redirect_cas()
            return werkzeug.utils.redirect(get_base_url() + '/auth_cas')

        if menu:
            request.context['menu'] = menu
        menu_data = request.registry['ir.ui.menu'].load_menu(
            request.cr, request.uid, context=request.context)
        return request.render('web.webclient_bootstrap',
                              qcontext={'menu_data': menu_data})

    def get_config(self, dbname):
        """ Retrieves the module config for the CAS authentication. """
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            icp = registry.get('ir.config_parameter')
            config = {
                'login_cas': icp.get_param(cr, openerp.SUPERUSER_ID,
                                           'cas_auth.cas_activated'),
                'host': icp.get_param(cr, openerp.SUPERUSER_ID,
                                      'cas_auth.cas_server'),
                'port': icp.get_param(cr, openerp.SUPERUSER_ID,
                                      'cas_auth.cas_server_port'),
                'cas_service': icp.get_param(cr, openerp.SUPERUSER_ID,
                                             'cas_auth.cas_service'),
                'base_url': icp.get_param(cr, openerp.SUPERUSER_ID,
                                          'web.base.url'),
                'auto_create': icp.get_param(cr, openerp.SUPERUSER_ID,
                                             'cas_auth.cas_create_user'),
            }

        return config

    def cas_authenticate(self, req, dbname, cur_url,
                         cas_host, auto_create, ticket):
        """ Checks if the user attempts to authenticate is
        authorized to do it and, if it is, authenticate him. """
        # cas_server = cas_host + ':' + cas_port
        cas_server = cas_host
        service_url = urllib.quote(cur_url, safe='')
        # The login function, from pycas, check if the ticket given by
        # CAS is a real ticket. The login of the user
        # connected by CAS is returned.

        status, idUser, cookie = login(cas_server, service_url, ticket)
        result = False

        if idUser and status == 0:
            cr = pooler.get_db(dbname).cursor()
            registry = RegistryManager.get(dbname)
            users = registry.get('res.users')
            ids = users.search(cr, SUPERUSER_ID, [('login', '=', idUser)])

            assert len(ids) < 2

            # We check if the user authenticated have an OpenERP account or if
            # the auto_create field is True
            if ids or auto_create == 'True':
                if ids:
                    user_id = ids[0]
                # If the user have no account, we create one
                else:
                    user_id = users.create(
                        cr, SUPERUSER_ID, {'name': idUser.capitalize(),
                                           'login': idUser})

                # A random key is generated in order to verify if the
                # login request come from here or if the user
                # try to authenticate by any other way
                cas_key = randomString(
                    16, '0123456789abcdefghijklmnopqrstuvwxyz')

                users.write(cr, SUPERUSER_ID, [user_id], {'cas_key': cas_key})
                cr.commit()

                login_and_redirect(dbname, idUser, cas_key)

                result = {'status': status,
                          'session_id': req.session_id}
            else:
                result = {'status': status,
                          'fail': True,
                          'session_id': req.session_id}

            cr.close()

        if not result:
            result = {'status': status}

        return result

    def cas_redirect(self, cas_host, service_url, opt="gateway", secure=1):
        """ Send redirect to client.  This function does
        not return, i.e. it teminates this script. """
        cas_url = cas_host + "/login?service=" + service_url
        _logger.info(cas_url)
        urllib.urlopen(cas_url)
        if opt in ("renew", "gateway"):
            cas_url += "&%s=true" % opt
        return werkzeug.utils.redirect(cas_url)

    @http.route('/auth_cas', type='http', auth='none')
    def cas_start(self, app=None, ticket=None, **q):
        dbname = getattr(request.session, 'db', None)
        if not dbname:
            return werkzeug.utils.redirect(get_base_url() + '/')

        config = self.get_config(dbname)
        if config['login_cas']:
            service_url = config['cas_service']
#             _logger.info('service_url----------------------' + service_url)
#             app = self.getQueryString(service_url, 'app')
            if app:
                service_url = app

            if not ticket and app:
                ticket = self.getQueryString(app, 'ticket')

            callback_url = self.delCASTicket(
                app) if app else self.delCASTicket(service_url)

            if not ticket:
                return self.cas_redirect(config['host'], callback_url)

            res = self.cas_authenticate(
                request, dbname, callback_url, config['host'],
                config['auto_create'], ticket)
            if res['status'] != 0:
                return self.cas_redirect(config['host'], callback_url)
            elif res.get('fail', False):
                return self.cas_redirect(config['host'], callback_url)
            else:
                if app:
                    return werkzeug.utils.redirect(callback_url)
                else:
                    return werkzeug.utils.redirect(get_base_url() + '/web')
        return werkzeug.utils.redirect(get_base_url() + '/adminlogin')

    def getQueryString(self, service_url, param=None):
        if param:
            u = urlparse(service_url)
            query = parse_qs(u.query)
            value = query.get(param, None)
            if value:
                return value[0]
            return False
        return False

    def delCASTicket(self, service_url):
        u = urlparse(service_url)
        query = parse_qs(u.query)
        query.pop('ticket', None)
        url = urlunparse(u._replace(query=urlencode(query, True)))

        if service_url.rfind('#') != -1:
            params = service_url.split('#')[1]
            url += '#' + params
        return url

    @http.route('/adminmanage', type='http', auth="none")
    def web_adminmanage(self, redirect=None, **kw):
        dbname = getattr(request.session, 'db', None)
        if not dbname:
            return werkzeug.utils.redirect(get_base_url() + '/')

        config = self.get_config(dbname)
        if config['cas_service']:
            url = config['cas_service']
            ind = url.find(':', 9)
            if ind > -1:
                return werkzeug.utils.redirect(url[:ind] + '/adminmanage', 303)

    @http.route('/adminlogin', type='http', auth="none")
    def web_adminlogin(self, redirect=None, **kw):
        return self.web_login(redirect, True)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, adminlogin=None, **kw):
        #         _logger.info('---------------------- web_login ')
        dbname = getattr(request.session, 'db', None)
        if not dbname:
            return werkzeug.utils.redirect(get_base_url() + '/')

        if adminlogin or request.httprequest.method == 'POST':
            Session().logout()
            main.ensure_db()
            if request.httprequest.method == 'GET' and \
                    redirect and request.session.uid:
                return werkzeug.utils.redirect(redirect)

            if not request.uid:
                request.uid = openerp.SUPERUSER_ID

            values = request.params.copy()
            if not redirect:
                redirect = get_base_url() + '/web?' + \
                    request.httprequest.query_string
            values['redirect'] = redirect

            try:
                values['databases'] = http.db_list()
            except openerp.exceptions.AccessDenied:
                values['databases'] = None

            if request.httprequest.method == 'POST':
                old_uid = request.uid
                uid = request.session.authenticate(
                    request.session.db, request.params['login'],
                    request.params['password'])
                if uid is not False:
                    return werkzeug.utils.redirect(redirect)
                request.uid = old_uid
                values['error'] = "Wrong login/password"
            return request.render('web.login', values)

        config = self.get_config(dbname)
        if config['login_cas']:
            if redirect:
                # _logger.info('----------------------' + get_base_url() +
                # '/auth_cas?app=' + redirect)
                return werkzeug.utils.redirect(get_base_url() +
                                               '/auth_cas?app=' + redirect)
            else:
                return werkzeug.utils.redirect(get_base_url() + '/auth_cas')
        else:
            return werkzeug.utils.redirect(get_base_url() + '/web')


class Apps(openerp.addons.web.controllers.main.Apps):

    @http.route('/app', auth='user')
    def index(self, req):
        debug = '?debug' if req.debug else ''
        return werkzeug.utils.redirect('/web{0}'.format(debug))

    @http.route('/app/<app>', auth='none')
    def get_app_url(self, req, app, ticket=None):
        debug = '?debug' if req.debug else ''
        menu_name = False
        dbname = getattr(request.session, 'db', None)

        if ticket:
            CasController().cas_start(get_base_url() + '/app/' + app, ticket)
        else:
            # request.session.logout()
            # request.session.db = getattr(request.session, 'db', False)
            request.session.uid = None

        if not request.session.uid:
            return werkzeug.utils.redirect(get_base_url() +
                                           '/web/login?redirect=' +
                                           get_base_url() + '/app/' + app)
#         CasController().web_login(get_base_url() + '/app/' + app)

        if app:
            _logger.info(
                '---- Login by AppURL - User: ' + str(request.session.login))
            ir_ui_menu = request.registry['ir.ui.menu']
            try:
                cr = pooler.get_db(dbname).cursor()
                menu_id = ir_ui_menu.get_id_by_name(
                    cr, request.session.uid, app)
                menu_name = ir_ui_menu.get_name_by_3digi(
                    cr, request.session.uid, app)
            except ValueError:
                menu_id = False

            if not menu_id:
                # return werkzeug.utils.redirect('/#action=login&loginerror=1')
                # result = {'error': _('You do not have permission to
                # access this page : %s') % (app)}
                return page_access_denied(app)
#                 return werkzeug.exceptions.Forbidden(result['error'])

            menu = 'menu_id=' + str(menu_id) if menu_id else ''
            debug = '&menu=' + \
                str(menu_name) if debug and menu_name else '?menu=' + \
                str(menu_name)

            return werkzeug.utils.redirect(get_base_url() +
                                           '/web{0}#{1}'.format(debug, menu))
        else:
            return werkzeug.utils.redirect(get_base_url() +
                                           '/web{0}'.format(debug))
