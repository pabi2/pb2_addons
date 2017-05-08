# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    # Enable crosstab feature in postgresql
    cr.execute("CREATE EXTENSION tablefunc;")
