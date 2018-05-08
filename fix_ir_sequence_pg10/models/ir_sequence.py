# -*- coding: utf-8 -*-
from openerp import models, fields


def _predict_nextval(self, seq_id):
    """Predict next value for PostgreSQL sequence without consuming it"""
    # Cannot use currval() as it requires prior call to nextval()
    query = """SELECT last_value,
                      (SELECT increment_by
                       FROM pg_sequences
                       WHERE sequencename = 'ir_sequence_%(seq_id)s'),
                      is_called
               FROM ir_sequence_%(seq_id)s"""
    if self.env.cr._cnx.server_version < 100000:
        query = """SELECT last_value, increment_by, is_called
                   FROM ir_sequence_%(seq_id)s"""
    self.env.cr.execute(query % {'seq_id': seq_id})
    (last_value, increment_by, is_called) = self.env.cr.fetchone()
    if is_called:
        return last_value + increment_by
    # sequence has just been RESTARTed to return last_value next time
    return last_value


class IRSequence(models.Model):

    _inherit = 'ir.sequence'

    number_next_actual = fields.Integer(
        compute='_get_number_next_actual',
        inverse='_set_number_next_actual',
    )

    def _get_number_next_actual(self):
        '''Return number from ir_sequence row when no_gap implementation,
        and number from postgres sequence when standard implementation.'''
        for element in self:
            if element.implementation != 'standard':
                element.number_next_actual = element.number_next
            else:
                seq_id = "%03d" % element.id
                element.number_next_actual = _predict_nextval(self, seq_id)

    def _set_number_next_actual(self):
        for record in self:
            record.write({'number_next': record.number_next_actual or 0})
