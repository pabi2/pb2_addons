# -*- coding: utf-8 -*-
from openerp import models, api, fields, exceptions, _
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


@job
def action_create_multi_supplier_invoices(session, model_name, res_id):
    try:
        session.pool[model_name].create_multi_supplier_invoices(
            session.cr, session.uid, [res_id], session.context
        )
        return _("Supplier Invoice created successfully")
    except Exception, e:
        raise RetryableJobError(e)


class ExpenseCreateMultiSupplierInvoice(PabiAsync, models.TransientModel):
    _inherit = "expense.create.multi.supplier.invoice"

    async_process = fields.Boolean(
        string='Run task in background?',
        default=True,
    )
    get_context = fields.Char()

    @api.multi
    def _save_context(self):
        self.get_context = self._context

    @api.multi
    def create_multi_supplier_invoices(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            ctx = eval(self.get_context)
            self = self.with_context(ctx)
            return super(ExpenseCreateMultiSupplierInvoice, self).\
                create_multi_supplier_invoices()
        # Enqueue
        if self.async_process:
            active_id = self._context.get('active_id')
            expense = self.env['hr.expense.expense'].browse(active_id)
            self._save_context()
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Create Supplier Invoices - %s' % expense.number
            uuid = action_create_multi_supplier_invoices.delay(
                session, self._name, self.id, description=description
            )
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref(
                'pabi_async_process.hr_expense_create_multi_supplier_invoice'
            )
            # Checking for running task, use the same signature as delay()
            task_name = "%s('%s', %s)" % ('action_create_multi_supplier_invoices',
                                          self._name, self.id)
            self._check_queue(task_name, desc=description, type='always')
        else:
            return super(ExpenseCreateMultiSupplierInvoice, self).\
                create_multi_supplier_invoices()
