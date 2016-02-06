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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class account_invoice(models.Model):

    _inherit = "account.invoice"

    is_deposit = fields.Boolean('Advance', readonly=True)

    @api.multi
    def action_cancel(self):
        """ For Advance (is_deposit=True), do not allow cancellation
        if advance amount has been deducted on following invoices"""
        for inv in self:
            if inv.is_deposit and inv.sale_ids.invoiced_rate:  # Other invoices exists
                raise except_orm(
                    _('Warning!'),
                    _("""Cancellation of advance invoice is not allowed!
                    Please cancel all following invoices first."""))
        res = super(account_invoice, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
