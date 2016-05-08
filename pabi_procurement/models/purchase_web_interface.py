# -*- coding: utf-8 -*-

from openerp import models, api
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
    def send_pd_test(self):
        ConfParam = self.env['ir.config_parameter']
        url = ConfParam.get_param('pabiweb_url')
        print url
        alfresco = xmlrpclib.ServerProxy(url)

        doc = self.encode_base64('PR_2015011901.pdf')
        att1 = self.encode_base64('PR_2015011901.pdf')
        att2 = self.encode_base64('PR_2015011901.pdf')

        arg = {
            'action': '1',
            'pdNo': 'PD16000002',
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
    def send_pd(self, PD):
        ConfParam = self.env['ir.config_parameter']
        url = ConfParam.get_param('pabiweb_url')
        alfresco = xmlrpclib.ServerProxy(url)
        doc_name = 'PR_2015011901.pdf'
        doc = self.encode_base64(doc_name)
        attachment = []
        for pd_att in PD.attachment_ids:
            pd_attach = {
                'name': pd_att.name,
                'content': pd_att.file
            }
            attachment.append(pd_attach)
        pr_name = ''
        for pd_line in PD.line_ids:
            for pd_pr_line in pd_line.purchase_request_lines:
                pr_name += pd_pr_line.request_id.name + ','
            pr_name = pr_name[:-1]
        arg = {
            'action': '1',
            'pdNo': PD.name,
            'sectionId': str(PD.line_ids[0].section_id.id),
            'prNo': pr_name,
            'docType': 'PD1',
            'objective': PD.objective,
            'total': PD.amount_total,
            'reqBy': '002648',
            'appBy': '001509',
            'doc': {
                'name': doc_name,
                'content': doc
            },
            'attachments': attachment,
        }
        result = alfresco.ord.create(arg)
        return result