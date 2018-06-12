from openerp.http import request
from openerp.addons.web.controllers.main import DataSet
import time


class ReportDataSet(DataSet):
    def _call_kw(self, model, method, args, kwargs):
        Config = request.env['ir.config_parameter']
        file_path = Config.get_param("report_locust.filepath")
        status = Config.get_param("report_locust.active")
        seconds = Config.get_param("report_locust.seconds")
        rpc_request = [
            str(request.env[model].search.__code__.co_varnames),
            str(args),
            str(kwargs),
        ]
        start = time.time()
        res = super(ReportDataSet, self)._call_kw(model, method, args, kwargs)
        exec_time = time.time() - start
        if file_path and status == 'True':
            if exec_time > float(seconds):
                with open(file_path+'lc_report.txt', 'a+') as f:
                    f.write('\nExecution Time: %s seconds\nMethod: %s.%s' %
                            (exec_time, request.env[model]._name, method))
                    f.write('\n%s\n' % ','.join(rpc_request))
                    f.close()
        return res
