# -*- coding: utf-8 -*-
import psycopg2
import time
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    special_type = fields.Selection(
        selection_add=[('doctype', 'Doctype Sequence')]
    )

    @api.model
    def next_by_doctype(self):
        # Check if doctype in context is valid
        doctype_id = self._context.get('doctype_id', False)
        if doctype_id:
            doctype = self.env['res.doctype'].browse(doctype_id)
            sequence_id = doctype.sequence_id.id
            if sequence_id:
                return super(IrSequence, self).next_by_id(sequence_id)
        return False

    @api.model
    def next_by_id(self, sequence_id):
        number = self.next_by_doctype()
        return number or super(IrSequence, self).next_by_id(sequence_id)

    @api.model
    def next_by_code(self, sequence_code):
        EXCEPTION = ('account.analytic.account', 'account.reconcile')
        if sequence_code in EXCEPTION:
            return super(IrSequence, self).next_by_code(sequence_code)
        number = self.next_by_doctype()
        return number or super(IrSequence, self).next_by_code(sequence_code)

    @api.multi
    def _next(self):
        self._cr.execute("SAVEPOINT next_sequence")
        try:
            res = super(IrSequence, self)._next()
            self._cr.execute("RELEASE SAVEPOINT next_sequence")
            return res
        except psycopg2.OperationalError:
            # Let's retry 3 times, each to wait 0.5 seconds
            retry = self._context.get('retry', 1)
            if retry <= 5:
                time.sleep(0.5)
                retry += 1
                self._cr.commit()
                return self.with_context(retry=retry)._next()
            self._cr.execute("RELEASE SAVEPOINT next_sequence")
            raise ValidationError(
                _('Waiting for next number, please try again!'))
        except Exception:
            self._cr.execute("RELEASE SAVEPOINT next_sequence")
            raise


class IrSequenceFiscalyear(models.Model):
    _inherit = 'account.sequence.fiscalyear'

    prefix = fields.Char(
        related='sequence_id.prefix',
        string='Prefix',
    )
    implementation = fields.Selection(
        [('standard', 'Standard'),
         ('no_gap', 'No gap'), ],
        related='sequence_id.implementation',
        string='Implementation',
    )
    number_next = fields.Integer(
        related='sequence_id.number_next',
        string='Next Number',
    )
