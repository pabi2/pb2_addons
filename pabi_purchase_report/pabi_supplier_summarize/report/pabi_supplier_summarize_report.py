# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiSupplierSummarizeReport(models.Model):
    _name = 'pabi.supplier.summarize.report'
    _description = 'Pabi Supplier Summarize Report'
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
        (
        select count(id)
        from purchase_order
        where partner_id = rp.id
        and state != 'cancel'
        ) as partner_po_count,
        (
        select sum(wa2.eval_receiving::integer)
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) as partner_sum_eval_receiving,
        (
        select sum(wa2.eval_quality::integer)
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) as partner_sum_eval_quality,
        (
        select sum(wa2.eval_service::integer)
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) as partner_sum_eval_service,
        (
        select (((sum(wa2.eval_receiving::float)) /
        (count(wa2.id) * 3)) * 3)::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) as partner_sum_avg_eval_receiving,
        (
        select (sum(wa2.eval_quality::float) /
        count(wa2.id))::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) as partner_sum_avg_eval_quality,
        (
        select (((sum(wa2.eval_service::float)) /
        (count(wa2.id) * 2)) * 2)::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) as partner_sum_avg_eval_service,
        (
        (
        select (((sum(wa2.eval_receiving::float)) /
        (count(wa2.id) * 3)) * 3)::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) +
        (
        select (sum(wa2.eval_quality::float) /
        count(wa2.id))::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) +
        (
        select (((sum(wa2.eval_service::float)) /
        (count(wa2.id) * 2)) * 2)::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        )
        ) as total_avg,
        case when
        (
        (
        select (((sum(wa2.eval_receiving::float))/(count(wa2.id)*3))*3)::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) +
        (
        select (sum(wa2.eval_quality::float) / count(wa2.id))::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        ) +
        (
        select (((sum(wa2.eval_service::float))/(count(wa2.id)*2))*2)::float
        from purchase_work_acceptance wa2
        left join purchase_order po2
        on po2.id = wa2.order_id
        where po2.partner_id = rp.id
        and po2.state != 'cancel'
        )
        ) >= 3.00
        then
        'Pass'
        else
        'Fail'
        end as result
        from purchase_work_acceptance wa
        left join purchase_order po on po.id = wa.order_id
        left join res_partner rp on rp.id = po. partner_id
        left join res_partner_title rpt on rpt.id = rp.title
        )""" % (self._table, ))
