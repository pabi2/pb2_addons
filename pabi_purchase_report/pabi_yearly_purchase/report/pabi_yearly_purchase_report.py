# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiYearlyPurchaseReport(models.Model):
    _name = 'pabi.yearly.purchase.report'
    _description = 'Pabi Yearly Purchase Report'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT
        to_char(pd.create_date,'YYYY') year_name,
        ou.name ou_name,
        pm.name method,
        COUNT(pd.id) pd_count,
        SUM(pd.amount_total) amount_total,
        rc.name currency,
        (SELECT af.id FROM account_fiscalyear af
            WHERE af.name = to_char(pd.create_date,'YYYY')) fiscalyear_id
        FROM purchase_requisition pd
        LEFT JOIN operating_unit ou
        ON ou.id = pd.operating_unit_id
        LEFT JOIN purchase_method pm
        ON pm.id = pd.purchase_method_id
        LEFT JOIN res_currency rc
        ON rc.id = pd.currency_id
        WHERE pd.purchase_method_id IS NOT NULL
        GROUP BY ou.id,
        pm.name,
        rc.name,
        to_char(pd.create_date,'YYYY'),
        (SELECT af.id FROM account_fiscalyear af
            WHERE af.name = to_char(pd.create_date,'YYYY'))
        ORDER BY ou.id
        )""" % (self._table, ))
