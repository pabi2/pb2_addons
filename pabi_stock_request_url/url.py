# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug.utils


class StockRequestURL(http.Controller):
    @http.route('/stock_request/', type='http', auth='public')
    def pabiweb_to_stock_request(self, **kw):
        Action = request.registry.get('ir.model.data')
        Param = request.registry.get('ir.config_parameter')
        action_id = Action.search(request.cr, SUPERUSER_ID,
                                  [('module', '=', 'stock_request'),
                                   ('name', '=', 'action_my_stock_request')])
        action = Action.browse(request.cr, SUPERUSER_ID, action_id)
        param_id = Param.search(request.cr, SUPERUSER_ID,
                                [('key', '=', 'web.base.url')])
        param = Param.browse(request.cr, SUPERUSER_ID, param_id)
        ext_url = """/web?toolbar=hide&#page=0&limit=80
            &view_type=list&model=stock.request&action="""
        url = param.value + ext_url + str(action.res_id)
        return werkzeug.utils.redirect(url)
