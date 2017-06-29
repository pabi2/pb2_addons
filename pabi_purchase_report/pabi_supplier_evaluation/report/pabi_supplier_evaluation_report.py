# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiSupplierEvaluationReport(models.Model):
    _name = 'pabi.supplier.evaluation.report'
    _description = 'Pabi Supplier Evaluation Report'
    _auto = False

    # purchase_type_id = fields.Many2one(
    #     'purchase.type',
    #     string='Purchase Type',
    # )
    # purchase_method_id = fields.Many2one(
    #     'purchase.method',
    #     string='Purchase Type',
    # )
    # date_from = fields.Date(string='Contract Start Date')
    # date_to = fields.Date(string='Contract End Date')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        select
        wa.id,
        rp.search_key as partner_code,
        concat(rpt.name,' ',rp.name) as partner_name,
        po.name as po_no,
        wa.name as wa_no,
        wa.date_contract_end,
        wa.date_receive,
        wa.eval_service,
        wa.eval_quality,
        wa.eval_receiving,
        case
        when (-1 * DATE_PART('day', wa.date_contract_end ::timestamp -
            wa.date_receive::timestamp)) > 0
        then
        -1 * DATE_PART('day', wa.date_contract_end ::timestamp -
            wa.date_receive::timestamp)
        else
        0
        end
        as delay_day
        from purchase_work_acceptance wa
        left join purchase_order po on po.id = wa.order_id
        left join res_partner rp on rp.id = po. partner_id
        left join res_partner_title rpt on rpt.id = rp.title
        )""" % (self._table, ))
