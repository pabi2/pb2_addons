# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    installment_date = fields.Date(
        string='Installment Date',
    )
    interval = fields.Integer(
        string='Interval',
    )

    @api.multi
    def mock_trigger_workflow(self, signal):
        """ Because openerplib can't call workflow directly, we mock it """
        self.signal_workflow(signal)
        return True

    @api.multi
    def mock_action_invoice_create(self):
        self.ensure_one()
        self.action_invoice_create()
        return True

    @api.model
    def mock_prepare_purchase_invoice_plan(
            self, purchase_id, installment_date=False,
            num_installment=1,
            installment_amount=False, interval=1, interval_type='month',
            invoice_mode='change_price', use_advance=False,
            advance_percent=0.0, use_deposit=False,
            advance_account=False, use_retention=False):

        self = self.with_context(active_model=self._name,
                                 active_id=purchase_id)
        purchase = self.env['purchase.order'].browse(purchase_id)
        value = self.env['account.account'].name_search(advance_account,
                                                        operator='=')
        if value and len(value) == 1:
            purchase.write({'account_deposit_supplier': value[0][0]})

        # Mock wizard
        Wizard = self.env['purchase.create.invoice.plan']
        res = Wizard.default_get([])
        res['num_installment'] = num_installment
        res['invoice_mode'] = invoice_mode
        res['installment_date'] = installment_date or \
            fields.Date.context_today(self)
        res['interval'] = interval or 1
        res['interval_type'] = interval_type or 'month'
        res['use_advance'] = use_advance
        res['use_deposit'] = use_deposit
        res['use_retention'] = use_retention
        wizard = Wizard.create(res)
        wizard._onchange_plan()
        # Simulate onchange on other params
        if not wizard.installment_amount and installment_amount:
            wizard.installment_amount = installment_amount
        wizard._onchange_installment_config()
        # Now, installment is crated as <newID> we need to make it persistant
        installments = []
        for line in wizard.installment_ids:
            if line.installment == 0:
                line.percent = advance_percent
                line._onchange_percent()
            installments.append((0, 0, line._convert_to_write(line._cache)))
        wizard.installment_ids = False  # remove it first, and rewrite by line
        wizard.write({'installment_ids': installments})
        wizard.do_create_purchase_invoice_plan()
        return True

    @api.multi
    def mork_invoice_paid(self):
        self.ensure_one()
        # Update fully_invoiced = true in purchase order line
        self._cr.execute("""
            UPDATE purchase_order_line
            SET fully_invoiced = true
            WHERE order_id = %s""" % self.id)

        # Update invoice = paid
        self._cr.execute("""
            UPDATE account_invoice
            SET state = 'paid', supplier_invoice_number = 'COD Migration',
                payment_type = 'transfer'
            WHERE source_document = '%s'""" % self.name)
        return True

    @api.multi
    def mork_purchase_done(self):
        self.write({'state': 'done'})
        return True

    @api.multi
    def mork_update_create_uid(self):
        """
        Use for update create uid
        require >> purchase_id, force_done_reason
        """
        self.ensure_one()
        if self.create_uid.login != self.force_done_reason:
            User = self.env['res.users']
            user = User.search([('login', '=', self.force_done_reason)])
            if not user:
                raise UserError(
                    _('There are not user code %s in the system'
                      % self.force_done_reason))
            if len(user) > 1:
                raise UserError(
                    _('There are multiple user code %s in the system'
                      % self.force_done_reason))
            self._cr.execute("""
                UPDATE purchase_order
                SET create_uid = %s
                WHERE id = %s""" % (user.id, self.id))
        return True

    @api.multi
    def mork_clear_force_done_reason(self):
        """
        Use for clear force done reason
        """
        self.ensure_one()
        self.force_done_reason = False
        return True
