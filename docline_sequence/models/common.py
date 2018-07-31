# -*- coding: utf-8 -*-
from openerp import fields, api


class DoclineCommon(object):

    @api.model
    def _compute_docline_seq(self, docline, fk, doc_id):
        """ Recompute docline sequence by doc_id """
        sql = """
            update %s a
            set docline_seq = new_seq
            from (select id, docline_seq,
                  row_number() over(order by (sequence, id)) as new_seq
                  from %s where %s = %s) seq
            where seq.id = a.id
        """ % (docline, docline, fk, doc_id, )
        self._cr.execute(sql)
        return True

    @api.model
    def _recompute_all_docline_seq(self, doc, doc_line, fk):
        sql = """
            select distinct b.%s
            from %s a
            join %s b on b.%s = a.id
            where b.docline_seq = 0
        """ % (fk, doc, doc_line, fk)
        self._cr.execute(sql)
        doc_ids = [x[0] for x in self._cr.fetchall()]
        for doc_id in doc_ids:
            self._compute_docline_seq(doc_line, fk, doc_id)


class DoclineCommonSeq(object):
    _order = 'sequence, id'

    docline_seq = fields.Integer(
        string='#',
        readonly=True,
        default=0,
        help="Sequence auto generated after document is confirmed",
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
