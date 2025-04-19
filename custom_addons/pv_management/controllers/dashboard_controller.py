# File: controllers/dashboard_controller.py
from odoo import http
from odoo.http import request


class PVDashboardController(http.Controller):
    @http.route('/pv_management/dashboard', type='http', auth='user', website=True)
    def pv_dashboard(self, **kw):
        """Render the dashboard"""
        # Create a dashboard record
        dashboard = request.env['pv.dashboard'].sudo().create({'name': 'Dashboard'})

        values = {
            'dashboard': dashboard,
        }
        return request.render('pv_management.pv_dashboard_template', values)

    @http.route('/pv_management/chart_data/<string:chart_type>', type='json', auth='user')
    def get_chart_data(self, chart_type, **kw):
        """Get chart data for AJAX updates"""
        dashboard = request.env['pv.dashboard'].sudo().create({'name': 'Dashboard'})

        if chart_type == 'installation_states':
            return {
                'data': dashboard.installation_states_chart,
                'type': 'pie'
            }
        elif chart_type == 'reclamation_monthly':
            return {
                'data': dashboard.reclamation_monthly_chart,
                'type': 'bar'
            }
        elif chart_type == 'intervention_states':
            return {
                'data': dashboard.intervention_states_chart,
                'type': 'pie'
            }
        elif chart_type == 'alarms_by_type':
            return {
                'data': dashboard.alarms_by_type_chart,
                'type': 'pie'
            }

        return {'error': 'Invalid chart type'}