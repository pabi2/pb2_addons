# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        for voucher in self:
            taxbranchs = []
            for line in voucher.line_ids:
                if line.amount or line.amount_wht or line.amount_retention:
                    taxbranchs.append(line.supplier_invoice_taxbranch_id.id)
            if len(list(set(taxbranchs))) > 1:
                raise UserError(_('Mixing invoices of different '
                                  'tax branch is not allowed!'))
        result = super(AccountVoucher, self).proforma_voucher()
        return result


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.model
    def get_suppl_inv_taxbranch(self, move_line_id):
        move_line = self.env['account.move.line'].\
            browse(move_line_id)
        return (move_line.invoice and
                move_line.invoice.taxbranch_id or False)

    @api.depends('move_line_id', 'voucher_id', 'amount')
    def _compute_supplier_invoice_taxbranch(self):
        for line in self:
            if line.move_line_id:
                line.supplier_invoice_taxbranch_id =\
                    self.get_suppl_inv_taxbranch(line.move_line_id.id)

    supplier_invoice_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        compute='_compute_supplier_invoice_taxbranch',
        string='Taxbranch',
        store=True,
    )


class AccountVoucherTax(models.Model):
    _inherit = "account.voucher.tax"

    @api.model
    def move_line_get(self, voucher_id):
        """ Normal Tax: Use invoice's tax branch for tax move line
            WHT: Use a centralized tax branch """
        res = super(AccountVoucherTax, self).move_line_get(voucher_id)
        voucher = self.env['account.voucher'].browse(voucher_id)
        taxbranch_id = False
        wht_taxbranch_id = voucher.partner_id.property_wht_taxbranch_id.id
        for line in voucher.line_ids:
            if line.amount or line.amount_wht or line.amount_retention:
                taxbranch_id = line.supplier_invoice_taxbranch_id.id
        if voucher.partner_id.property_tax_move_by_taxbranch:
            for r in res:
                if r['tax_code_type'] == 'wht' and \
                        voucher.partner_id.property_wht_taxbranch_id:
                    r.update({'taxbranch_id': wht_taxbranch_id})
                else:
                    r.update({'taxbranch_id': taxbranch_id})
        return res
