# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp import tools


class DocumentAuditlogLogLine(models.Model):
    _name = 'document.auditlog.log.line'
    _auto = False

    status = fields.Char(
        string=u'Status',
    )
    user_id = fields.Many2one(
        'res.users',
        string=u"Changed By",
    )
    model_id = fields.Many2one(
        'ir.model',
        string=u"Model",
    )
    res_id = fields.Integer(u"Resource ID")
    date = fields.Datetime(
        string=u'Changed Date',
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        ondelete='cascade',
        string=u"Field",
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT
                logline.id as id,
                logline.new_value as status,
                log.user_id as user_id,
                log.model_id as model_id,
                log.res_id as res_id,
                log.create_date as date,
                logline.field_id as field_id
            FROM
                auditlog_log_line as logline
            JOIN auditlog_log log
                ON (log.id = logline.log_id)
            JOIN ir_model_fields field
                ON (field.id = logline.field_id)
            WHERE field.name = 'state'
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(), ))
