from odoo import models, fields, api, _
import uuid
import logging

_logger = logging.getLogger(__name__)
class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    def _default_access_token(self):
        return uuid.uuid4().hex

    name = fields.Char(string='Request Reference', required=True, copy=False, index=True, default=lambda self: _('New'))
    is_periodic_inspection = fields.Boolean(string='Es una inspección periódica')
    expiration_date = fields.Date(string='Fecha de caducidad')
    work_done = fields.Text(string='Trabajos realizados', track_visibility='onchange')
    materials_used = fields.Text(string='Materiales usados', track_visibility='onchange')
    observations = fields.Text(string='Observaciones', track_visibility='onchange')
    task_ids = fields.One2many('maintenance.task', 'maintenance_request_id', string='Tareas')
    worker_signature = fields.Binary(string='Firma trabajador', widget='image')
    client_signature = fields.Binary(string='Firma cliente', widget='image')
    access_token = fields.Char('Invitation Token', default=_default_access_token)

    def action_open_signature_page(self):
        self.ensure_one()

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.access_token or self._default_access_token()
        url = f"{base_url}/my/maintenance_order/{self.id}?access_token={token}"
        _logger.info(f"Generated URL: {url}")
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }


    @api.model
    def create(self, vals):
        record = super(MaintenanceRequest, self).create(vals)
        record._update_notes()
        return record

    def write(self, vals):
        res = super(MaintenanceRequest, self).write(vals)
        self._update_notes()
        return res

    def _update_notes(self):
        for record in self:
            notes = {
                'Trabajos realizados': record.work_done or '',
                'Materiales usados': record.materials_used or '',
                'Observaciones': record.observations or ''
            }

            for note_title, note_content in notes.items():
                existing_note = self.env['mail.message'].search([
                    ('model', '=', 'maintenance.request'),
                    ('res_id', '=', record.id),
                    ('subtype_id', '=', self.env.ref('mail.mt_note').id),
                    ('body', 'like', f'{note_title}:%')
                ], limit=1)

                note_body = f"{note_title}: {note_content}"

                if existing_note:
                    existing_note.body = note_body
                else:
                    record.message_post(body=note_body, subtype_id=self.env.ref('mail.mt_note').id)