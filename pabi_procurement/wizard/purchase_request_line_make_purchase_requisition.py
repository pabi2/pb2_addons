# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError
import ast


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _get_requisition_line_search_domain(self, requisition, item):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _get_requisition_line_search_domain(requisition, item)
        res.append(('id', '=', item.id))  # Use id will ensure no merge
        return res

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_purchase_requisition_line(pr, item)
        taxes = [(4, tax.id) for tax in item.line_id.tax_ids]
        res.update({
            'price_unit': item.price_unit,
            'price_standard': item.price_unit,
            'schedule_date': item.date_required,
            'fixed_asset': item.fixed_asset,
            'product_name': item.name,
            'tax_ids': taxes
        })
        return res

    @api.model
    def _prepare_purchase_requisition(self, picking_type_id, company_id):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_purchase_requisition(picking_type_id, company_id)
        pr_line_obj = self.env['purchase.request.line']
        active_id = self._context['active_ids'][0]
        req_id = pr_line_obj.browse(active_id).request_id
        condition = req_id.purchase_condition_id.id
        condition_detail_id = req_id.purchase_condition_detail_id.id
        vals = {
            'user_id': req_id.responsible_uid.id,
            'description': req_id.description,
            'objective': req_id.objective,
            'currency_id': req_id.currency_id.id,
            'currency_rate': req_id.currency_rate,
            'purchase_type_id': req_id.purchase_type_id.id,
            'purchase_method_id': req_id.purchase_method_id.id,
            'purchase_price_range_id': req_id.purchase_price_range_id.id,
            'purchase_condition_id': condition,
            'purchase_condition_detail_id': condition_detail_id,
            'purchase_condition_detail': req_id.purchase_condition_detail,
            'total_budget_value': req_id.total_budget_value,
            'purchase_prototype_id': req_id.purchase_prototype_id.id,
            'request_uid': req_id.requested_by.id,
            'assign_uid': req_id.assigned_to.id,
            'date_approve': req_id.date_approve,
            'request_ref_id': req_id.request_ref_id.id,
            'delivery_address': req_id.delivery_address,
        }
        res.update(vals)
        return res

    @api.model
    def _prepare_item(self, line):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_item(line)
        res.update({
            'price_unit': line.price_unit,
            'tax_ids': line.tax_ids.ids,
            'date_required': line.date_required,
            'fixed_asset': line.fixed_asset,
        })
        return res

    @api.model
    def _check_line_reference(self, pr_lines):
        cur_ref = []
        for pr_line in pr_lines:
            if hasattr(pr_line.request_id, 'request_ref_id'):
                if pr_line.request_id.request_ref_id.id not in cur_ref \
                        and pr_line.request_id.request_ref_id.id:
                    cur_ref.append(pr_line.request_id.request_ref_id.id)
            else:
                if 'None' not in cur_ref:
                    cur_ref.append('None')
        if len(cur_ref) > 1:
            raise UserError(
                _("Can't create CfBs by PR lines with many references.")
            )
        return True

    @api.model
    def _requisition_filter(self, pr_lines):
        pr_ref = []
        domain = []
        for pr_line in pr_lines:
            if pr_line.request_id.request_ref_id and \
                pr_line.request_id.request_ref_id not in pr_ref:
                    pr_ref.append(pr_line.request_id.request_ref_id.id)
        if len(pr_ref) > 0:
            domain = {
                'requisition_id': [
                    ('request_ids', 'in', pr_ref)
                ]
            }
        return {'domain': domain}

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequestLineMakePurchaseRequisition,
                    self).default_get(fields)
        request_line_obj = self.env['purchase.request.line']
        request_line_ids = self.env.context['active_ids'] or []
        pr_lines = request_line_obj.browse(request_line_ids)
        self._check_line_reference(pr_lines)
        self._requisition_filter(pr_lines)
        return res

    @api.model
    def _prepare_attachment_line(self, line, requisition_id):
        return {
            'res_id': requisition_id,
            'res_model': 'purchase.requisition',
            'name': line.name,
            'description': line.description,
            'type': line.type,
            'url': line.url,
            'datas': line.datas or False,
        }

    @api.model
    def _prepare_committee_line(self, line, requisition_id):
        return {
            'requisition_id': requisition_id,
            'name': line.name,
            'sequence': line.sequence,
            'position': line.position,
            'committee_type_id': line.committee_type_id.id,
        }

    @api.model
    def _prepare_all_attachments(self, requisition, requests):
        attachments = []
        for request in requests:
            for line in request.attachment_ids:
                attachment_line = self._prepare_attachment_line(line,
                                                                requisition.id)
                attachments.append([0, False, attachment_line])
        return attachments

    @api.model
    def _prepare_all_committees(self, requisition, requests):
        committees = []
        for request in requests:
            for line in request.committee_ids:
                committee_line = self._prepare_committee_line(line,
                                                              requisition.id)
                committees.append([0, False, committee_line])
        return committees

    @api.multi
    def check_status_request_line(self):
        for item in self.item_ids:
            if item.request_id.state != 'approved':
                raise UserError(
                    _("Some Request hasn't been accepted yet : %s"
                      % (item.request_id.name,))
                )
            elif item.line_id.requisition_state != 'none':
                raise UserError(
                    _("Each Request bid status should be 'No Bid' : %s"
                      % (item.request_id.name,))
                )
            elif item.line_id.request_id.request_ref_id:
                if not self.purchase_requisition_id:
                    raise UserError(
                        _("You can't create new CfBs from the PR line with"
                          " PR reference : %s" % (item.request_id.name,))
                    )
                elif not item.product_id:
                    raise UserError(
                        _("You have to select the product if the request has a"
                          " PR reference : %s" % (item.request_id.name,))
                    )
            elif not item.line_id.request_id.request_ref_id \
                    and self.purchase_requisition_id:
                raise UserError(
                    _("You cannot add PR Line with no PR reference to CfBs."
                      " PR reference : %s" % (item.request_id.name,))
                )
        return True

    @api.multi
    def make_purchase_requisition(self):
        res = False
        if self.check_status_request_line():
            res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
                make_purchase_requisition()
            domain = ast.literal_eval(res['domain'])
            requisition_id = list(set(domain[0][2]))[0]
            requisition = self.env['purchase.requisition'].\
                browse(requisition_id)
            requests = [item.line_id.request_id for item in self.item_ids]
            requests = list(set(requests))  # remove duplicated requests
            # Merge attachment and committee into Purchase Requisition
            committees = self._prepare_all_committees(requisition, requests)
            attachments = self._prepare_all_attachments(requisition, requests)
            requisition.write({
                'committee_ids': committees,
                'attachment_ids': attachments,
                'exclusive': 'exclusive',
            })
        return res


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"

    price_unit = fields.Float(
        'Unit Price',
        track_visibility='onchange',
    )
    price_standard = fields.Float(
        'Standard Price',
    )
    tax_ids = fields.Many2many(
        'account.tax',
        'purchase_request_make_requisition_taxes_rel',
        'item_id',
        'tax_id',
        string='Taxes',
        readonly=True,
    )
    fixed_asset = fields.Boolean(
        string='Fixed Asset',
    )
    date_required = fields.Date(
        string='Request Date',
    )
