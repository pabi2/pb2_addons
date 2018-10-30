# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tax_mismatch = fields.Boolean(
        string='Tax Mismatch',
        compute='_compute_tax_mismatch',
        help="True if untaxed + tax != total",
    )

    @api.multi
    def _compute_tax_mismatch(self):
        for rec in self:
            amount = rec.amount_untaxed + rec.amount_tax
            if float_compare(amount, rec.amount_total, 2) == 0:
                rec.tax_mismatch = False
            else:
                rec.tax_mismatch = True
        return True

    @api.v7
    def fix_tax_rounding(self, cr, uid, ids, context=None):
        """ This method will,
            1) Change tax counding method
            2) Calc Tax
            3) Set rounding method back
        """
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company_id = user.company_id.id
        Company = self.pool.get('res.company')
        old_method = user.company_id.tax_calculation_rounding_method
        new_method = (old_method == 'round_per_line') and \
            'round_globally' or 'round_per_line'
        vals = {'tax_calculation_rounding_method': new_method}
        Company.write(cr, uid, [company_id], vals, context=context)
        self._amount_all(cr, uid, ids, False, False, context=context)
        vals = {'tax_calculation_rounding_method': old_method}
        Company.write(cr, uid, [company_id], vals, context=context)
        return True
