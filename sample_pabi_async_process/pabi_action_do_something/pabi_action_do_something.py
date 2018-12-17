# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PabiActionDoSomething(models.TransientModel):
    """ PABI Action for Do Something """
    _name = 'pabi.action.do.something'
    _inherit = 'pabi.action'

    # Wizard Criteria
    employee_id = fields.Many2one(
        'hr.employee',
        string='Dept. Manager',
        required=True,
        help="Employee name to update Department Manager",
    )

    @api.model
    def do_something(self, employee_id):
        """ This must by of type @api.model, all paramas must not be value """
        # Do simple update Dpeartment Manager
        departments = self.env['hr.department'].search([])
        departments.write({'manager_id': employee_id})
        # --
        # Return records being processes and message
        records = departments
        result_msg = _('Finished doing something')
        return (records, result_msg)

    @api.multi
    def pabi_action(self):
        """ Interited Function, to use Job Queue """
        self.ensure_one()
        # Prepare job information
        process_xml_id = 'sample_pabi_async_process.do_something'  # <--
        job_desc = _('Do Something...')
        func_name = 'do_something'  # <--
        # Prepare kwargs, the params for method action_generate
        kwargs = {'employee_id': self.employee_id.id, }
        # Call the function
        res = super(PabiActionDoSomething, self).\
            pabi_action(process_xml_id, job_desc, func_name, **kwargs)
        return res
