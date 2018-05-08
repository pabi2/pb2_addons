# -*- coding: utf-8 -*
from openerp.report import report_sxw
from openerp.tools.translate import _


class PabiLongTermInvestmentReport(report_sxw.rml_parse):

    def __init__(self, cursor, uid, name, context):
        super(PabiLongTermInvestmentReport, self).__init__(
            cursor, uid, name, context=context,
        )
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('Long Term Investment'),
        })

    def _get_account(self, data):
        return self._get_info(data, 'account_id', 'account.account')

    def _get_partner(self, data):
        return self._get_info(data, 'partner_id', 'res.partner')

    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field, False)
        return self.pool.get(model).browse(self.cr, self.uid, info)

    def set_context(self, objects, data, ids, report_type=None):
        """
        Populate a long_term_investment_line attribute on each browse record
        """
        # Reading form
        date_print = data.get('form', {}).get('date_print', False)
        account = self._get_account(data)
        partner = self._get_partner(data)

        investment_lines = self._compute_investment_lines(account.id,
                                                          date_print,
                                                          partner.id)
        objects = self.pool.get('account.account').browse(self.cr, self.uid,
                                                          account.id)
        self.localcontext.update({
            'account': account,
            'date_print': date_print,
            'partner': partner,
            'investment_lines': investment_lines,
        })

        return super(PabiLongTermInvestmentReport, self).set_context(
            objects, data, account.id, report_type=report_type)

    def _compute_investment_lines(self, account_id, date_print, partner_id):
        move_line_obj = self.pool.get('account.move.line')
        domain = [('account_id', '=', account_id)]
        if date_print:
            domain += [('date', '<=', date_print)]
        if partner_id:
            domain += [('partner_id', '=', partner_id)]
        move_line_ids = move_line_obj.search(self.cr, self.uid, domain)
        return move_line_ids and \
            self._get_investment_line_datas(move_line_ids) or []

    def _get_investment_line_datas(self, move_line_ids,
                                   order='ml.partner_id, i.id'):
        sql = """
            SELECT ml.partner_id,
                i.id AS investment_id,
                i.name,
                i.date_approve,
                i.description,
                i.total_capital,
                i.total_share,
                i.nstda_share,
                i.price_unit,
                i.price_subtotal,
                ml.name AS invoice_desc,
                ml.date AS date_invoice,
                ml.debit - ml.credit AS amount_invoice,
                ml.id AS move_line_id,
                ml.ref AS invoice_number
            FROM account_move_line AS ml
            JOIN res_partner_investment i ON ml.investment_id = i.id
            JOIN account_period p on ml.period_id = p.id
            WHERE ml.id IN %s"""
        sql += (" ORDER BY %s" % (order,))
        try:
            self.cr.execute(sql, (tuple(move_line_ids),))
            res = self.cr.dictfetchall()
        except Exception:
            self.cr.rollback()
            raise
        return res or []
