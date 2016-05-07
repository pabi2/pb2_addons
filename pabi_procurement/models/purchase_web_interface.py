# -*- coding: utf-8 -*-

from openerp import models, api
import xmlrpclib
import base64


class PurchaseWebInterface(models.Model):
    _name = "purchase.web.interface"
    _description = "Purchase Web Interface"

    @api.model
    def encode_base64(self, filename):
        with open(filename) as f:
            encoded = base64.b64encode(f.read())
            return encoded

    @api.model
    def send_pd(self):
        ConfParam = self.env['ir.config_parameter']
        url = ConfParam.get_param('pabiweb_url')
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