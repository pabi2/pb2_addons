# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _, exceptions
from openerp.exceptions import ValidationError
import ast


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    # def _requisition_filter(self):
    #     requisition_ref = ()
    #     pr_lines = self.item_ids.line_id
    #     for pr_line in pr_lines:
    #         if pr_line.request_id.request_ref_id and \
    #            pr_line.request_id.request_ref_id not in requisition_ref:
    #                 request_lines = self.env['purchase.request.line'].search(
    #                     [
    #                         (
    #                             'request_id',
    #                             'in',
    #                             (pr_line.request_id.request_ref_id.id,)
    #                         )
    #                     ]
    #                 )
    #                 cfb_lines = self.env['purchase.requisition.line'].search(
    #                     [
    #                         (
    #                             'purchase_request_lines',
    #                             'in',
    #                             request_lines._ids
    #                         )
    #                     ]
    #                 )
    #                 for cfb_line in cfb_lines:
    #                     requisition_ref.append(cfb_line.requisition_id.id)
    #     if len(requisition_ref) > 0:
    #         domain = [
    #             ('state', '=', 'draft'),
    #             ('id', 'in', requisition_ref)
    #         ]
    #     # res['domain'] = domain
    #     return domain

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
            'tax_ids': taxes,
            'fiscalyear_id': item.line_id.fiscalyear_id.id or False,
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
            # 'purchase_prototype_id': req_id.purchase_prototype_id.id,
            'prototype_type': req_id.prototype_type,
            'request_uid': req_id.requested_by.id,
            'assign_uid': req_id.assigned_to.id,
            'date_approve': req_id.date_approve,
            'request_ref_id': req_id.request_ref_id.id,
            'delivery_address': req_id.delivery_address,
        }
        res.update(vals)
        #  assign user's picking type and ou to central purchase requisition
        if req_id.is_central_purchase:
            type_obj = self.env['stock.picking.type']
            user_ou_id = self.env['res.users'].operating_unit_default_get(
                self._uid)
            company_id = self.env.context.get('company_id') or \
                self.env.user.company_id.id
            types = type_obj.search([
                ('code', '=', 'incoming'),
                ('warehouse_id.company_id', '=', company_id),
                ('warehouse_id.operating_unit_id', '=', user_ou_id.id)
            ])
            if not types:
                types = type_obj.search([('code', '=', 'incoming'),
                                         ('warehouse_id', '=', False)
                                         ('warehouse_id.operating_unit_id', '=', user_ou_id.id)])
            user_picking_type = types[:1]
            res.update({
                'operating_unit_id': user_ou_id.id,
                'picking_type_id': user_picking_type.id,
                'company_id': company_id,
                'is_central_purchase': req_id.is_central_purchase,
                'exclusive': 'multiple',
                'multiple_rfq_per_supplier': True,
            })
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
            raise ValidationError(
                _("Can't create CfBs by PR lines with many references.")
            )
        return True

    @api.model
    def default_get(self, fields):
        request_line_obj = self.env['purchase.request.line']
        request_line_ids = self._context.get('active_ids', [])
        add_context = self._context.copy()
        for line in request_line_obj.browse(request_line_ids):
            if line.request_id.is_central_purchase:
                user_ou_id = self.env['res.users'].\
                    operating_unit_default_get(self._uid)
                is_central = user_ou_id
                add_context['is_central'] = is_central
                break
        res = super(PurchaseRequestLineMakePurchaseRequisition,
                    self.with_context(add_context)).default_get(fields)
        pr_lines = request_line_obj.browse(request_line_ids)
        self._check_line_reference(pr_lines)
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
            'attach_by': line.attach_by.id,
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
                raise ValidationError(
                    _("Some Request hasn't been accepted yet : %s"
                      % (item.request_id.name,))
                )
            elif item.line_id.requisition_state != 'none':
                raise ValidationError(
                    _("Each Request bid status should be 'No Bid' : %s"
                      % (item.request_id.name,))
                )
            elif item.line_id.state != 'open':
                raise ValidationError(
                    _("Some request line is already closed' : %s"
                      % (item.request_id.name,))
                )
            elif item.line_id.requisition_state != 'none':
                raise ValidationError(
                    _("Each Request bid status should be 'No Bid' : %s"
                      % (item.request_id.name,))
                )
            elif item.line_id.request_id.request_ref_id:
                # if not self.purchase_requisition_id:
                #     raise ValidationError(
                #         _("You can't create new CfBs from the PR line with"
                #           " PR reference : %s" % (item.request_id.name,))
                #     )
                if not item.product_id:
                    raise ValidationError(
                        _("You have to select the product if the request has a"
                          " PR reference : %s" % (item.request_id.name,))
                    )
            elif not item.line_id.request_id.request_ref_id \
                    and self.purchase_requisition_id:
                raise ValidationError(
                    _("You cannot add PR Line with no PR reference to CfBs."
                      " PR reference : %s" % (item.request_id.name,))
                )
        return True

    @api.multi
    def make_purchase_requisition_original(self):
        pr_obj = self.env['purchase.requisition']
        pr_line_obj = self.env['purchase.requisition.line']
        company_id = False
        picking_type_id = False
        requisition = False
        res = []
        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise exceptions.Warning(
                    _('Enter a positive quantity.'))
            line_company_id = line.company_id \
                and line.company_id.id or False
            if company_id is not False \
                    and line_company_id != company_id \
                    and not line.request_id.is_central_purchase:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same company.'))
            else:
                company_id = line_company_id

            line_picking_type = line.request_id.picking_type_id
            if picking_type_id is not False \
                    and line_picking_type.id != picking_type_id \
                    and not line.request_id.is_central_purchase:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same picking type.'))
            elif line.request_id.is_central_purchase:
                Warehouse = self.env['stock.warehouse']
                warehouses = Warehouse.search([
                    ('operating_unit_id', '=', self.operating_unit_id.id)
                ])
                for warehouse in warehouses:
                    picking_type_id = warehouse.in_type_id.id
                    break
            else:
                picking_type_id = line_picking_type.id

            if self.purchase_requisition_id:
                requisition = self.purchase_requisition_id
            if not requisition:
                preq_data = self._prepare_purchase_requisition(picking_type_id,
                                                               company_id)
                requisition = pr_obj.create(preq_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_requisition_line_search_domain(requisition,
                                                              item)
            available_pr_lines = pr_line_obj.search(domain)
            if available_pr_lines:
                pr_line = available_pr_lines[0]
                new_qty = pr_line.product_qty + item.product_qty
                pr_line.product_qty = new_qty
                pr_line.purchase_request_lines = [(4, line.id)]
            else:
                po_line_data = self._prepare_purchase_requisition_line(
                    requisition, item)
                pr_line_obj.create(po_line_data)
            res.append(requisition.id)

        return {
            'domain': "[('id','in', [" + ','.join(map(str, res)) + "])]",
            'name': _('Purchase requisition'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def make_purchase_requisition(self):
        res = False
        if self.check_status_request_line():
            res = self.make_purchase_requisition_original()
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

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            # self.product_qty = 1
            self.name = name
