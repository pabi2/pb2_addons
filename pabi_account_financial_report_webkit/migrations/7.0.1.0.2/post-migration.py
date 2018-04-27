# -*- coding: utf-8 -*-
def migrate(cr, version):
    if not version:
        # only run at first install
        cr.execute("UPDATE account_move_line as acm "
                   " SET last_rec_date ="
                   "     (SELECT date from account_move_line"
                   "          WHERE reconcile_id =  acm.reconcile_id"
                   "              AND reconcile_id IS NOT NULL"
                   "          ORDER BY date DESC LIMIT 1)"
                   " WHERE last_rec_date is null;")

        cr.execute("UPDATE account_move_line as acm "
                   " SET last_rec_date ="
                   "     (SELECT date from account_move_line"
                   "          WHERE reconcile_partial_id"
                   "                             = acm.reconcile_partial_id"
                   "              AND reconcile_partial_id IS NOT NULL"
                   "          ORDER BY date DESC LIMIT 1)"
                   " WHERE last_rec_date is null;")
