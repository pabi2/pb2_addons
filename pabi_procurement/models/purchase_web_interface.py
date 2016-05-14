# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning as UserError
import xmlrpclib
import base64
import os
import inspect


class PurchaseWebInterface(models.Model):
    _name = "purchase.web.interface"
    _description = "Purchase Web Interface"

    @api.model
    def encode_base64(self, filename):
        current_path = inspect.getfile(inspect.currentframe())
        directory_path = os.path.dirname(os.path.abspath(current_path))
        path = os.path.expanduser(directory_path+'/../data/'+filename)
        with open(path) as f:
            encoded = base64.b64encode(f.read())
            return encoded

    @api.model
    def check_pdf_extension(self, filename):
        if '.pdf' not in filename:
            filename += '.pdf'
        return filename

    @api.model
    def send_pbweb_requisition_test(self):
        ConfParam = self.env['ir.config_parameter']
        url = ConfParam.get_param('pabiweb_url')
        username = ConfParam.get_param('pabiweb_username')
        password = ConfParam.get_param('pabiweb_password')
        connect_string = "http://%s:%s@%s" % (username, password, url)
        alfresco = xmlrpclib.ServerProxy(connect_string, allow_none=True)
        doc = self.encode_base64('PR_2015011901.pdf')
        att1 = self.encode_base64('PR_2015011901.pdf')
        att2 = self.encode_base64('PR_2015011901.pdf')

        arg = {
            'action': '1',
            'pdNo': 'PD16000003',
            'sectionId': '1',
            'prNo': 'PR16000001,PR16000002',
            'docType': 'PD1',
            'objective': 'Buy Something 1 piece',
            'total': '100000.00',
            'reqBy': '002648',
            'appBy': '001509',
            'doc': {
                'name': 'PD16000002.pdf',
                'content': doc
            },
            'attachments': [
                {
                    'name': 'A.pdf',
                    'content': att1,
                },
                {
                    'name': 'B.pdf',
                    'content': att2,
                }
            ]
        }
        result = alfresco.ord.create(arg)
        return result

    @api.model
    def send_pbweb_requisition(self, requisition):
        User = self.env['res.users']
        users = User.search([('id', '=', self._uid)])
        assert len(requisition) == 1, \
            "Only 1 Call for Bids could be done at a time."
        ConfParam = self.env['ir.config_parameter']
        Attachment = self.env['ir.attachment']
        url = ConfParam.get_param('pabiweb_url')
        username = users.login
        password = ConfParam.get_param('pabiweb_password')
        connect_string = "http://%s:%s@%s" % (username, password, url)
        alfresco = xmlrpclib.ServerProxy(connect_string, allow_none=True)
        pd_file = Attachment.search([
            ('res_id', '=', requisition.id),
            ('res_model', '=', 'purchase.requisition'),
        ])
        if len(pd_file) != 1:
            raise UserError(
                _("Only 1 Requisition Form could be done at a time.")
            )
        doc_name = pd_file.name
        doc = pd_file.datas
        request_usr = User.search([('id', '=', requisition.request_uid.id)])
        assign_usr = User.search([('id', '=',  requisition.assign_uid.id)])
        attachment = []
        for pd_att in requisition.attachment_ids:
            pd_attach = {
                'name': self.check_pdf_extension(pd_att.name),
                'content': pd_att.file
            }
            attachment.append(pd_attach)
        pr_name = ''
        for pd_line in requisition.line_ids:
            for pd_pr_line in pd_line.purchase_request_lines:
                pr_name += pd_pr_line.request_id.name + ','
            pr_name = pr_name[:-1]
        arg = {
            'action': '1',
            'pdNo': requisition.name,
            'sectionId': str(requisition.line_ids[0].section_id.id),
            'prNo': pr_name,
            'docType': 'PD1',
            'objective': requisition.objective or '',
            'total': str(requisition.amount_total),
            'reqBy': request_usr,
            'appBy': assign_usr,
            'doc': {
                'name': self.check_pdf_extension(doc_name),
                'content': doc
            },
            'attachments': attachment,
        }
        result = alfresco.ord.create(arg)
        if not result['success']:
            raise UserError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        return result

    @api.model
    def send_pbweb_action_request(self, request, action):
        users = self.env['res.users'].search([('id', '=', self._uid)])
        assert len(request) == 1, \
            "Only 1 Purchase Request could be done at a time."
        ConfParam = self.env['ir.config_parameter']
        url = ConfParam.get_param('pabiweb_url')
        username = users.login
        password = ConfParam.get_param('pabiweb_password')
        connect_string = "http://%s:%s@%s" % (username, password, url)
        alfresco = xmlrpclib.ServerProxy(connect_string, allow_none=True)
        if action == "accept":
            send_act = "C2"
        else:
            send_act = "X2"
        result = alfresco.req.action(request.name, send_act, users.login)
        if not result['success']:
            raise UserError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        return result
