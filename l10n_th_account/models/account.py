# -*- coding: utf-8 -*-
#
#    Author: Kitti Upariphutthiphong
#    Copyright 2014-2015 Ecosoft Co., Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields, api


class account_tax(models.Model):

    _inherit = 'account.tax'

    is_undue_tax = fields.Boolean(
        string='Undue Tax',
        default=False,
        help="""This is a undue tax account.
                The tax point will be deferred to the time of payment""",
    )
    is_wht = fields.Boolean(
        string='Withholding Tax',
        help="Tax will be withhold and will be used in Payment",
    )
    threshold_wht = fields.Float(
        string='Threshold Amount',
        help="""Withholding Tax will be applied only if base amount more
                or equal to threshold amount""",
    )
    refer_tax_id = fields.Many2one(
        'account.tax',
        string='Counterpart Tax',
        ondelete='restrict',
        help="Counterpart Tax for payment process",
    )

    @api.v7
    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None,
                    partner=None, force_excluded=False, context=None):
        if context is None:
            context = {}
        payment_type = context.get('type', False)
        if payment_type not in ('receipt', 'payment'):  # Invoice
            taxes = taxes.filtered(lambda r: not r.is_wht)  # Remove all WHT
        res = super(account_tax, self).compute_all(
            cr, uid, taxes, price_unit, quantity, product=None,
            partner=None, force_excluded=False)
        return res

    @api.v8
    def compute_all(self, price_unit, quantity, product=None,
                    partner=None, force_excluded=False):
        return self._model.compute_all(
            self._cr, self._uid, self, price_unit, quantity,
            product=product, partner=partner, force_excluded=force_excluded,
            context=self._context)

    @api.one
    @api.depends('is_wht')
    def onchange_is_wht(self):
        self.is_undue_tax = False

    @api.one
    @api.depends('is_undue_tax')
    def onchange_is_undue_tax(self, is_undue_tax):
        self.is_wht = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
