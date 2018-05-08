# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug.utils


class MyProjectURL(http.Controller):
    """ URL = http://localhost:8069/myproject?project=PROJECT-A """
    @http.route('/myproject/', type='http', auth='public')
    def myproject_to_project(self, **kw):
        project = kw.get('project', False)
        Project = request.registry.get('res.project')
        pids = Project.name_search(request.cr, SUPERUSER_ID,
                                   project, operator='=')
        if len(pids) != 1:
            return False
        p = Project.browse(request.cr, SUPERUSER_ID, pids[0][0])
        # action
        Action = request.registry.get('ir.model.data')
        action_id = Action.search(
            request.cr, SUPERUSER_ID,
            [('module', '=', 'pabi_my_project'),
             ('name', '=', 'action_myproject_to_project')])
        action = Action.browse(request.cr, SUPERUSER_ID, action_id)
        # URL
        url = "/web?toolbar=hide&#model=res.project&view_type=form"
        ext_url = "&id=%s&action=%s" % (p.id, action.res_id)
        return werkzeug.utils.redirect(url + ext_url)
