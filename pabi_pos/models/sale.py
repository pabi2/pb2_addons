# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancel_id = fields.Many2one('res.partner', 'Cancel by')
    cancel_date = fields.Datetime('Cancel Date')
    cancel_reason = fields.Char('Cancel Reason')
    
    @api.model
    def _prepare_invoice(self, order, lines):
        invoice_vals = super(SaleOrder, self)._prepare_invoice(order, lines)
        workflow = order.workflow_process_id
        if not workflow:
            return invoice_vals
        invoice_vals['number_preprint'] = order.origin
        invoice_vals['date_invoice'] = order.date_order
        invoice_vals['date_document'] = order.date_order
        invoice_vals['date_due'] = order.date_order
        return invoice_vals

    @api.onchange('workflow_process_id')
    def onchange_workflow_process_id(self):
        if not self.workflow_process_id:
            return
        wf = self.workflow_process_id
        if wf.operating_unit_id:
            self.operating_unit_id = wf.operating_unit_id
        if wf.warehouse_id:
            self.warehouse_id = wf.warehouse_id
        if wf.taxbranch_id:
            self.taxbranch_id = wf.taxbranch_id
        return super(SaleOrder, self).onchange_workflow_process_id()

    @api.model
    def default_get(self, field_list):
        res = super(SaleOrder, self).default_get(field_list)
        process_id = self._context.get('default_workflow_process_id', False)
        if process_id:
            process = self.env['sale.workflow.process'].browse(process_id)
            res['taxbranch_id'] = process.taxbranch_id.id
        return res

    @api.multi
    def action_ship_create(self):
        res = super(SaleOrder, self).action_ship_create()
        for order in self.filtered('workflow_process_id'):
            pickings = order.picking_ids.\
                filtered('workflow_process_id.validate_picking')
            pickings.validate_picking()
            order.filtered(lambda l: l.invoiced and l.shipped).action_done()
        return res

    @api.multi
    def action_invoice_create(self):
        self.ensure_one()
        if self.origin:
            invoice_preprint = self.env['account.invoice'].search([
                ('number_preprint', '=', self.origin)
            ])
            if invoice_preprint:
                raise ValidationError(
                    _('Source Document/Number Preprint %s is not unique!') %
                    self.origin)
        res = super(SaleOrder, self).action_invoice_create()
        invoices = self.env['account.invoice'].browse(res)
        for invoice in invoices:
            if invoice.workflow_process_id.validate_invoice:
                invoice.signal_workflow('invoice_open')
                # Validate payment too
                journal = invoice.workflow_process_id.voucher_journal_id

                # kittiu: May be we never through bank payment
                # bank = invoice.workflow_process_id.partner_bank_id
                # voucher = self._auto_validate_payment(invoice, journal)
                self._auto_validate_payment(invoice, journal)
                # self._auto_validate_bank_receipt(voucher, journal, bank)
        return res

    @api.model
    def _auto_validate_payment(self, invoice, journal):
        current_period = self.env['account.period'].find(invoice.date_invoice)
        # Create Payment and Validate It!
        voucher = self.env['account.voucher'].create({
            'date': invoice.date_invoice,
            'amount': invoice.amount_total,
            'account_id': journal.default_debit_account_id.id,
            'partner_id': invoice.partner_id.id,
            'type': 'receipt',
            'receipt_type': 'cash',
            'date_value': invoice.date_due,
            'period_id': current_period.id,
            'date_document': invoice.date_document,
            'number_preprint': invoice.number_preprint,
            'journal_id': journal.id,
            'operating_unit_id': invoice.operating_unit_id.id,
        })
        val = voucher.\
            with_context({
                'filter_invoices': [invoice.id]}).\
            onchange_partner_id(
                voucher.partner_id.id,
                voucher.journal_id.id,
                voucher.amount,
                voucher.currency_id.id,
                voucher.type,
                voucher.date
            )
        voucher_lines = [(0, 0, line) for
                         line in val['value']['line_cr_ids']]
        voucher.write({'line_cr_ids': voucher_lines})
        if not voucher.writeoff_amount:
            voucher.signal_workflow('proforma_voucher')
        return voucher

    @api.model
    def _auto_validate_bank_receipt(self, voucher, journal, bank):
        move_lines = voucher.move_ids.filtered(
            lambda l:
            l.account_id == journal.default_debit_account_id and
            l.debit > 0.0 and
            not l.reconcile_id
        )
        total_amount = sum(move_lines.mapped('debit'))
        # Create Bank Receipt and Validate it
        receipt = self.env['account.bank.receipt'].create({
            'date': fields.Date.context_today(self),
            'journal_id': journal.id,
            'currency_id':
            journal.currency.id or journal.company_id.currency_id.id,
            'partner_bank_id': bank.id,
            'bank_account_id': bank.journal_id.default_debit_account_id.id,
            'manual_total_amount': total_amount,
            'total_amount': total_amount,
            'bank_intransit_ids': [(6, 0, move_lines.ids)],
        })
        receipt.validate_bank_receipt()

    @api.multi
    def post_process_pos_order(self):
        """ Use existing onchange to select configured fields """
        for pos in self:
            # As per WF configuration
            pos.onchange_workflow_process_id()
            # Partner
            wf = pos.workflow_process_id
            if not pos.partner_id:
                pos.partner_id = wf.pos_partner_id
            # onchange partner
            res = self.onchange_partner_id(pos.partner_id.id)
            values = res['value']
            pos.partner_invoice_id = values['partner_invoice_id']
            pos.pricelist_id = values['pricelist_id']
            pos.payment_term = values['payment_term']
            # order_line
            section = wf.res_section_id
            fund = wf.res_section_id.fund_ids and \
                wf.res_section_id.fund_ids[0] or False
            for line in pos.order_line:
                line.section_id = section
                line.fund_id = fund
                product = line.product_id
                line.activity_group_id = product.categ_id.activity_group_id
                line.activity_rpt_id = product.categ_id.activity_id

    def _get_pos_receipt(self):
        SEQUENCE = self.env['ir.sequence']
        date_fis = datetime.now() + relativedelta(months=3)
        fisyear = str(date_fis.strftime('%y'))
        if self.amount_tax == 0.00:
            prefix = 'RC'
        else:
            prefix = 'RT'

        sequence_id = SEQUENCE.search([('name','=','POS Receipt %s - %s'%(prefix,fisyear)),('prefix','=',prefix+'-PS'+fisyear)])
        if not sequence_id:
            sequence_id = SEQUENCE.create({'name': 'POS Receipt %s - %s'%(prefix,fisyear),
                                           'number_next': 1,
                                           'implementation': 'standard',
                                           'padding': 4,
                                           'number_increment': 1,
                                           'prefix': prefix+'-PS'+fisyear,
                                        })
        receipt_no = SEQUENCE.get_id(sequence_id.id)
        self.origin = receipt_no
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def default_get(self, field_list):
        res = super(SaleOrderLine, self).default_get(field_list)
        process_id = self._context.get('workflow_process_id', False)
        if process_id:
            process = self.env['sale.workflow.process'].browse(process_id)
            res['section_id'] = process.res_section_id.id
        return res
