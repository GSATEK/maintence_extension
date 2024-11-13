# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


from odoo import fields, http

from odoo.http import request

from odoo.addons.portal.controllers import portal
import logging
import binascii

_logger = logging.getLogger(__name__)

class PortalMaintenance(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'maintence_count' in counters:
            MaintenanceRequests = request.env['maintenance.request']
            has_access = MaintenanceRequests.check_access_rights('read', raise_exception=False)
            user = request.env.user
            domain = [('user_id', '=', user.id)]
            maint_count = MaintenanceRequests.search_count(domain) if has_access else 0

            values['maintence_count'] = str(maint_count) if has_access else '0'

        return values

    @http.route(['/my/maintenance_orders'], type='http', auth="user", website=True)
    def portal_my_maintenance_orders(self, state=None, **kwargs):
        domain = [('user_id', '=', request.uid)]
        if state:
            domain.append(('stage_id', '=', int(state)))
        maintenance_orders = request.env['maintenance.request'].sudo().search(domain)
        states = request.env['maintenance.stage'].sudo().search([])
        values = {
            'maintenance_orders': maintenance_orders,
            'states': states,
            'selected_state': int(state) if state else None,
        }
        return request.render('maintence_extension.portal_my_maintenance_orders', values)


    @http.route(['/my/maintenance_order/<int:order_id>'], type='http', auth="user", website=True)
    def portal_my_maintenance_order(self, order_id, **kwargs):
        maintenance_order = request.env['maintenance.request'].sudo().browse(order_id)
        if not maintenance_order.exists():
            return request.not_found()
        values = {
            'maintenance_order': maintenance_order,
        }
        return request.render('maintence_extension.portal_my_maintenance_order', values)

    @http.route('/my/maintenance_order/update', type='http', auth='user', methods=['POST'], csrf=True)
    def update_maintenance_order(self, **post):
        maintenance_order_id = int(post.get('id'))
        maintenance_order = request.env['maintenance.request'].browse(maintenance_order_id)

        if maintenance_order.exists():
            maintenance_order.write({
                'stage_id': int(post.get('stage_id')),
                'duration': float(post.get('duration')),
                'request_date': post.get('request_date'),
                'work_done': post.get('work_done'),
                'materials_used': post.get('materials_used'),
                'observations': post.get('observations'),
            })

            for task in maintenance_order.task_ids:
                task_state = post.get(f'state_{task.id}')
                if task_state == 'on':
                    task.write({'state': 'realizado'})
                else:
                    task.write({'state': 'pendiente'})

        return request.redirect('/my/maintenance_orders')

class MaintenanceOrderController(http.Controller):

    @http.route(['/my/maintenance_order/worker/sign/<int:order_id>'], type='json', auth="public", website=True)
    def sign_worker(self, order_id, name, signature, **kwargs):
        _logger.info(f"Signing maintenance order ID {order_id} with name {name}")
        maintenance_order = request.env['maintenance.request'].sudo().browse(order_id)
        if not maintenance_order.exists():
            return {'error': 'Maintenance order not found'}
        try:
            maintenance_order.write({
                'worker_signature': signature,
                'signed_by': name
            })

            return {
                'success': True,
                'force_refresh': True
            }
        except Exception as e:
            _logger.error(f"Error saving signature for maintenance order ID {order_id}: {e}")
            return {'error': 'Error saving signature'}


