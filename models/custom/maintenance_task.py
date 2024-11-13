from odoo import models, fields

class MaintenanceTask(models.Model):
    _name = 'maintenance.task'
    _description = 'Maintenance Task'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    tipo_mantenimiento_id = fields.Many2one('maintenance.type', string='Tipo de mantenimiento')
    time = fields.Float(string='Time')
    state = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('realizado', 'Realizado')
    ], string='Estado', default='pendiente')
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')