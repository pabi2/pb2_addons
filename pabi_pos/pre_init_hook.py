# -*- coding: utf-8 -*-


def pre_init_hook(cr):
    # Disable job schedule
    try:
        cr.execute("""
            update ir_cron set active = false
            where name = 'Automatic Workflow Job'
        """)
    except Exception:
        pass
