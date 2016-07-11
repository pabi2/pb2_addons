# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import xmlrpclib
import base64
import os
import inspect


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    @api.model
    def _get_request_info(self, data_dict):
        if 'org_id' in data_dict:
            Org = self.env['res.org']
            organization = Org.search([
                ('id', '=', data_dict['org_id']),
            ])
            for org in organization:
                type_id = False
                Warehouse = self.env['stock.warehouse']
                PType = self.env['stock.picking.type']
                warehouse = Warehouse.search([
                    ('operating_unit_id', '=', org.operating_unit_id.id),
                ])
                for wh in warehouse:
                    picking_type = PType.search([
                        ('warehouse_id', '=', wh.id),
                        ('code', '=', 'incoming'),
                    ])
                    for picking in picking_type:
                        type_id = picking.id
                        break
                    break
                data_dict.update({
                    'picking_type_id.id': type_id,
                    'operating_unit_id.id': org.operating_unit_id.id,
                })
                del data_dict['org_id']
                break
        return data_dict

    @api.model
    def generate_purchase_request(self, data_dict):
        ret = {}
        data_dict = self._get_request_info(data_dict)
        fields = data_dict.keys()
        data = data_dict.values()
        # Final Preparation of fields and data
        try:
            fields, data = self._finalize_data_to_load(fields, data)
            load_res = self.load(fields, data)
            res_id = load_res['ids'] and load_res['ids'][0] or False
            if not res_id:
                ret = {
                    'is_success': False,
                    'result': False,
                    'messages': [m['message'] for m in load_res['messages']],
                }
            else:
                res = self.browse(res_id)
                self.create_purchase_request_attachment(data_dict, res_id)
                self.create_purchase_request_committee(data_dict, res_id)
                ret = {
                    'is_success': True,
                    'result': {
                        'request_id': res.id,
                        'name': res.name,
                    },
                    'messages': _('PR has been created.'),
                }
                res.state = 'to_approve'
            self._cr.commit()
        except Exception, e:
            ret = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        return ret


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.model
    def done_order(self, af_info):
        # {
        #     'name': 'TE00017',
        #     'approve_uid': '002241',
        #     'action' : 'C1' or 'W2'
        #     'file_name': 'TE00017.pdf',
        #     'file_url': 'aaaaas.pdf',
        #     'comment': 'reject reason',
        # }
        user = self.env['res.users']
        Order = self.env['purchase.order']
        res = {}
        requisition = self.search([('name', '=', af_info['name'])])
        uid = user.search([('login', '=', af_info['approve_uid'])])
        if len(requisition) == 1:
            if af_info['action'] == 'C1':  # approve
                att_file = []
                try:
                    attachments = {
                        'requisition_id': requisition.id,
                        'name': af_info['file_name'],
                        'file_url': af_info['file_url'],
                    }
                    att_file.append([0, False, attachments])
                    today = fields.Date.context_today(self)
                    requisition.write({
                        'doc_approve_uid': uid.id,
                        'date_doc_approve': today,
                    })
                    for order in requisition.purchase_ids:
                        if order.order_type == 'quotation' \
                                and order.state not in ('draft', 'cancel'):
                            requisition.write({
                                'attachment_ids': att_file,
                            })
                            order.action_button_convert_to_order()
                            if order.state2 != 'done' or order.state != 'done':
                                order.write({
                                    'state': 'done',
                                    'state2': 'done',
                                    'doc_approve_uid': uid.id,
                                    'date_doc_approve': today,
                                })
                                purchase_order = Order.search([
                                    ('id', '=', order.order_id.id)
                                ])

                                for purchase in purchase_order:
                                    po_id = purchase.id
                                    committees = requisition.\
                                        _prepare_order_committees(po_id)
                                    purchase.write({
                                        'committee_ids': committees,
                                        'verify_uid': order.verify_uid.id,
                                        'date_verify': order.date_verify,
                                        'doc_approve_uid': uid.id,
                                        'date_doc_approve': today,
                                    })
                    if requisition.state != 'done':
                        requisition.tender_done()
                    res.update({
                        'is_success': True,
                        'result': True,
                    })
                except Exception, e:
                    res.update({
                        'is_success': False,
                        'result': False,
                        'messages': _(str(e)),
                    })
            else:  # reject
                try:
                    requisition.write({
                        'reject_reason_txt': af_info['comment'],
                    })
                    requisition.signal_workflow('open_rejected')
                    res.update({
                        'is_success': True,
                        'result': True,
                    })
                except Exception, e:
                    res.update({
                        'is_success': False,
                        'result': False,
                        'messages': _(str(e)),
                    })
        else:
            res.update({
                'is_success': False,
                'result': False,
                'messages': 'Cannot assign done state to Call for Bids.',
            })
        return res


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
        if '.pdf' not in filename and '.' not in filename:
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
        Employee = self.env['hr.employee']
        users = User.search([('id', '=', self._uid)])
        assert len(requisition) == 1, \
            "Only 1 Call for Bids could be done at a time."
        ConfParam = self.env['ir.config_parameter']
        if ConfParam.get_param('pabiweb_active') != 'TRUE':
            return False
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
        request_usr = User.search([('id', '=', requisition.user_id.id)])
        assign_usr = User.search([('id', '=', requisition.verify_uid.id)])
        employee = Employee.search([('user_id', '=', request_usr.id)])
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
        doc_type = requisition.get_doc_type()
        arg = {
            'action': '1',
            'pdNo': requisition.name,
            'sectionId': str(employee.section_id.id),
            'prNo': pr_name,
            'docType': doc_type.name,
            'objective': requisition.objective or '',
            'total': str(requisition.amount_total),
            'reqBy': request_usr.login,
            'appBy': assign_usr.login,
            'doc': {
                'name': self.check_pdf_extension(doc_name),
                'content': doc,
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
    def send_pbweb_action_request_test(self, request_name, action, user_name):
        ConfParam = self.env['ir.config_parameter']
        url = ConfParam.get_param('pabiweb_url')
        if ConfParam.get_param('pabiweb_active') != 'TRUE':
            return False
        password = ConfParam.get_param('pabiweb_password')
        connect_string = "http://%s:%s@%s" % (user_name, password, url)
        alfresco = xmlrpclib.ServerProxy(connect_string, allow_none=True)
        if action == "accept":
            send_act = "C2"
        else:
            send_act = "X2"
        result = alfresco.req.action(request_name, send_act, user_name)
        if not result['success']:
            raise UserError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        return result

    @api.model
    def send_pbweb_action_request(self, request, action):
        ConfParam = self.env['ir.config_parameter']
        if ConfParam.get_param('pabiweb_active') != 'TRUE':
            return False
        url = ConfParam.get_param('pabiweb_url')
        username = self.env.user.login
        password = ConfParam.get_param('pabiweb_password')
        connect_string = "http://%s:%s@%s" % (username, password, url)
        alfresco = xmlrpclib.ServerProxy(connect_string, allow_none=True)
        if action == "accept":
            send_act = "C2"
        else:
            send_act = "X2"
        comment = request.reject_reason_txt or ''
        result = alfresco.req.action(request.name, send_act, comment, username)
        if not result['success']:
            raise UserError(
                _("Can't send data to PabiWeb : %s" % (result['message'],))
            )
        return result
