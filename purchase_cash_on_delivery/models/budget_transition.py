# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class BudgetTransition(models.Model):
    """ For case COD
    - Do not return budgt when related Invoice / Stock Move is confirmed.
    - Do return budget when TP is created.
    As such, we want to skip do forward in such cases
    """
    _inherit = 'budget.transition'

    @api.model
    def do_forward(self, model, objects, obj_line_field=False):
        if model in ('account.invoice', 'stock.move'):
            prepaid = []
            if model == 'account.invoice':  # PO -> INV
                prepaid = objects.mapped('is_prepaid')
                # Only for document with state = paid (clearing perpayment)
                # allow to do_forward
                # objects = objects.filtered(lambda l: l.state == 'paid')
                # super(BudgetTransition, self).\
                #     do_forward(model, objects, obj_line_field=obj_line_field)
                # return
            # Case Picking
            if model == 'stock.move':  # PO -> INV
                prepaid = \
                    objects.mapped('purchase_line_id.order_id.is_prepaid')
            if len(prepaid) > 1:
                raise ValidationError(_('Mixing COD and non-COD not allowed.'))
            # If COD, do nothing
            elif prepaid and prepaid[0]:
                return  # Do nothing

        # Not COD
        return super(BudgetTransition, self).\
            do_forward(model, objects, obj_line_field=obj_line_field)
