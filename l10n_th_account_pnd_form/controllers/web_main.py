# -*- coding: utf-8 -*-
import base64
import simplejson
import time
import zlib

from openerp import http
from openerp.addons.web.controllers.main import Reports,\
    serialize_exception, content_disposition
from openerp.http import request


class Reports(Reports):
    @http.route('/web/report', type='http', auth="user")
    @serialize_exception
    def index(self, action, token):
        action = simplejson.loads(action)

        report_srv = request.session.proxy("report")
        context = dict(request.context)
        context.update(action["context"])

        report_data = {}
        report_ids = context.get("active_ids", None)
        if 'report_type' in action:
            report_data['report_type'] = action['report_type']
        if 'datas' in action:
            if 'ids' in action['datas']:
                report_ids = action['datas'].pop('ids')
            report_data.update(action['datas'])

        report_id = report_srv.report(
            request.session.db, request.session.uid, request.session.password,
            action["report_name"], report_ids,
            report_data, context)

        report_struct = None
        while True:
            report_struct = report_srv.report_get(
                request.session.db, request.session.uid,
                request.session.password, report_id)
            if report_struct["state"]:
                break

            time.sleep(self.POLLING_DELAY)

        report = base64.b64decode(report_struct['result'])
        if report_struct.get('code') == 'zlib':
            report = zlib.decompress(report)
        report_mimetype = self.TYPES_MAPPING.get(
            report_struct['format'], 'octet-stream')
        file_name = action.get('name', 'report')
        if 'name' not in action:
            reports = request.session.model('ir.actions.report.xml')
            res_id = reports.search(
                [('report_name', '=', action['report_name']), ],
                0, False, False, context)
            if len(res_id) > 0:
                file_name = reports.read(res_id[0], ['name'], context)['name']
            else:
                file_name = action['report_name']
        # Call hook to change filename
        if 'format' not in action:
            file_name = '%s.%s' % (file_name, report_struct['format'])
        else:
            if action.get('format'):
                file_name = '%s.%s' % (file_name, action.get('format'))
            else:
                file_name = '%s.%s' % (file_name, report_struct['format'])
        return request.make_response(
            report,
            headers=[
                ('Content-Disposition', content_disposition(file_name)),
                ('Content-Type', report_mimetype),
                ('Content-Length', len(report))],
            cookies={'fileToken': token})
