# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import except_orm


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )

    @api.model
    def default_get(self, fields):
        request_line_obj = self.env['purchase.request.line']
        request_line_ids = self._context.get('active_ids', [])
        active_model = self.env.context['active_model']
        res = super(PurchaseRequestLineMakePurchaseRequisition,
                    self).default_get(fields)

        if not request_line_ids:
            return res
        assert active_model == 'purchase.request.line', \
            'Bad context propagation'

        items = []
        for line in request_line_obj.browse(request_line_ids):
                items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items

        operating_unit_id = False
        for line in request_line_obj.browse(request_line_ids):
            line_operating_unit_id = line.request_id.operating_unit_id \
                and line.request_id.operating_unit_id.id or False
            if operating_unit_id is not False \
                    and line_operating_unit_id != operating_unit_id \
                    and not line.request_id.is_central_purchase:
                raise except_orm(
                    _('Could not process !'),
                    _('You have to select lines '
                      'from the same operating unit.'))
            else:
                operating_unit_id = line_operating_unit_id
        res['operating_unit_id'] = operating_unit_id

        return res
