# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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


class AccountInvoiceCancel(models.TransientModel):

    """ Ask a reason for the account invoice cancellation."""
    _name = 'account.invoice.cancel'
    _description = __doc__

    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False,
        size=500,
    )

    @api.one
    def confirm_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        invoice_ids = self._context.get('active_ids')
        if invoice_ids is None:
            return act_close
        assert len(invoice_ids) == 1, "Only 1 invoice expected"
        invoice = self.env['account.invoice'].browse(invoice_ids)
        invoice.cancel_reason_txt = self.cancel_reason_txt
        invoice.signal_workflow('invoice_cancel')
        return act_close
