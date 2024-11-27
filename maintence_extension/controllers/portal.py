# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging
from werkzeug.exceptions import Forbidden
import binascii
from lxml import etree

_logger = logging.getLogger(__name__)

class PortalMaintenance(CustomerPortal):

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
        access_token = kwargs.get('access_token')

        if not maintenance_order.exists():
            return request.not_found()

        if maintenance_order.access_token != access_token:
            raise Forbidden()

        google_maps_src = ''
        if maintenance_order.equipment_id.google_maps_link:
            try:
                iframe_html = maintenance_order.equipment_id.google_maps_link
                iframe_element = etree.fromstring(iframe_html)
                google_maps_src = iframe_element.get('src')
            except Exception as e:
                _logger.error("Error al procesar el iframe de Google Maps: %s", e)

        values = {
            'maintenance_order': maintenance_order,
            'google_maps_src': google_maps_src,
        }

        if maintenance_order.worker_signature:
            return request.render('maintence_extension.portal_my_maintenance_order_readonly', values)
        else:
            return request.render('maintence_extension.portal_my_maintenance_order', values)

    @http.route('/my/maintenance_order/update', type='json', auth='user', methods=['POST'], csrf=True)
    def update_maintenance_order(self, **post):
        maintenance_order_id = int(post.get('id'))
        maintenance_order = request.env['maintenance.request'].sudo().browse(maintenance_order_id)
        action = post.get('action')

        if maintenance_order.exists():
            update_values = {
                'request_date': post.get('request_date'),
                'observations': post.get('observations'),
            }

            if 'duration' in post and post.get('duration'):
                try:
                    update_values['duration'] = float(post.get('duration'))
                except ValueError:
                    update_values['duration'] = 0.0

            if 'stage_id' in post and post.get('stage_id') is not None:
                update_values['stage_id'] = int(post.get('stage_id'))

            if action == 'save':
                maintenance_order.sudo().write(update_values)
            elif action == 'finalize' and 'signature' in post:
                _logger.info('Firmado')
                if maintenance_order.worker_signature:
                    update_values['client_signature'] = post.get('signature')
                else:
                    update_values['worker_signature'] = post.get('signature')
                    pending_stage = request.env['maintenance.stage'].sudo().search(
                        [('name', '=', 'Pendiente de firma cliente')], limit=1)
                    if pending_stage:
                        update_values['stage_id'] = pending_stage.id


                if 'observations' in post:
                    _logger.info('Observaciones')
                    update_values['observations'] = post.get('observations')

                maintenance_order.sudo().write(update_values)

                if maintenance_order.worker_signature and maintenance_order.client_signature:
                    reparado_stage = request.env['maintenance.stage'].sudo().search([('name', '=', 'Reparado')],
                                                                                    limit=1)
                    if reparado_stage:
                        maintenance_order.sudo().write({'stage_id': reparado_stage.id})
                        maintenance_order.send_repaired_notification()

            for task_data in post.get('tasks', []):
                task_id = int(task_data['id'])
                task_state = task_data['state']
                task = request.env['maintenance.task'].sudo().browse(task_id)
                if task.exists():
                    if task_state == 'realizado':
                        task.sudo().write({'state': 'realizado'})
                    else:
                        task.sudo().write({'state': 'pendiente'})

        return {'success': True}

    @http.route('/my/maintenance_order/update_stage', type='json', auth='user', methods=['POST'], csrf=True)
    def update_maintenance_order_stage(self, **post):
        _logger.info(f"POST: {post}")
        maintenance_order_id = post.get('id')
        _logger.info(f"ID: {maintenance_order_id}")
        if maintenance_order_id is None:
            return {'success': False, 'error': 'No maintenance order ID provided'}

        maintenance_order_id = int(maintenance_order_id)
        maintenance_order = request.env['maintenance.request'].sudo().browse(maintenance_order_id)
        stage_id = request.env['maintenance.stage'].sudo().search([('name', '=', 'En progreso')], limit=1).id

        if maintenance_order.exists():
            maintenance_order.sudo().write({'stage_id': stage_id})

        return {'success': True}

    @http.route('/my/maintenance_order/products', type='json', auth='user')
    def get_products(self, maintenance_request_id=None):
        if maintenance_request_id:
            _logger.info(f"Received maintenance_request_id: {maintenance_request_id}")
        products = request.env['product.product'].search([])
        product_data = [{'id': product.id, 'name': product.name} for product in products]
        return {'products': product_data}

    @http.route('/my/maintenance_order/add_product', type='json', auth='user')
    def add_product(self, product_id, quantity, maintenance_request_id):
        _logger.info(
            f"Adding product with ID: {product_id}, Quantity: {quantity}, Maintenance Request ID: {maintenance_request_id}")
        if maintenance_request_id:
            request.env['maintenance.request.product'].create({
                'maintenance_request_id': maintenance_request_id,
                'product_id': product_id,
                'quantity': quantity,
            })
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Maintenance request ID not found'}

    @http.route('/my/maintenance_order/update_product', type='json', auth='user')
    def update_product(self, **kwargs):
        product_id = kwargs.get('id')
        product_template_id = kwargs.get('product_template_id')
        quantity = kwargs.get('quantity')

        _logger.info(
            f"Updating Maintenance Request Product: {product_id}, Product Template: {product_template_id}, Quantity: {quantity}")

        if not product_id or not product_template_id:
            return {'status': 'error', 'message': 'Product ID and Product Template ID are required'}

        product = request.env['maintenance.request.product'].browse(int(product_id))

        if product.exists():
            product.write({
                'product_id': int(product_template_id),
                'quantity': quantity,
            })
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Product not found'}

    @http.route('/my/maintenance_order/delete_product', type='json', auth='user')
    def delete_product(self, id):
        product = request.env['maintenance.request.product'].browse(id)
        if product:
            product.unlink()
            return {'status': 'success'}
        return {'status': 'error', 'message': 'Product not found'}