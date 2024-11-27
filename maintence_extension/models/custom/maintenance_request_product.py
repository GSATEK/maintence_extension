from odoo import models, fields

class MaintenanceRequestProduct(models.Model):
    _name = 'maintenance.request.product'
    _description = 'Maintenance Request Product'

    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    quantity = fields.Float(string='Cantidad', required=True)