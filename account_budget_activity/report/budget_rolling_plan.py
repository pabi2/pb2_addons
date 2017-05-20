# Here is the sample of rolling plan report, give current period_id = 24

# select row_number() over (order by period_id) as id,
# budget_method, user_id, fiscalyear_id,
# planned_amount,
# coalesce(pa1.id, pa2.id) as product_activity_id,
# activity_id, product_id, period_id, plan_period_id, actual_period_id
# from
# (select budget_method, user_id, fiscalyear_id,
# planned_amount,
# -- Dimensions
# activity_id, product_id, period_id, period_id as plan_period_id,
# 0 as actual_period_id
# from budget_plan_report
# where state in ('validate', 'done')
# UNION ALL
# select budget_method, user_id, fiscalyear_id,
# amount_pr_commit+amount_po_commit+amount_exp_commit+
#     amount_actual as planned_amount,
# -- Dimensions
# activity_id, product_id, period_id, 0 as plan_period_id,
# period_id as actual_period_id
# from budget_consume_report) a
# -- Join for product.activity
# left outer join product_activity pa1
# on pa1.temp_activity_id = a.activity_id
# left outer join product_activity pa2
# on pa2.temp_product_id = a.product_id
# and plan_period_id >= 24 and actual_period_id < 24
