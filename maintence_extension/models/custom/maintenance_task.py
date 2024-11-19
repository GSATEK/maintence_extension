from odoo import models, fields

class MaintenanceTask(models.Model):
    _name = 'maintenance.task'
    _description = 'Maintenance Task'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    maintenance_tpye = fields.Many2one('maintenance.type', string='Tipo de mantenimiento')
    time = fields.Float(string='Tiempo estimado')
    state = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('realizado', 'Realizado')
    ], string='Estado', default='pendiente')
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')