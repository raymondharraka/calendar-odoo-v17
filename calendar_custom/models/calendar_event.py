from odoo import models, fields, api
from odoo.tools import html2plaintext  # Utilidad de Odoo para esto


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # Campo computed que genera un bloque HTML mostrador del color.
    state_color = fields.Char(string="Color", compute="_compute_color_html", store=False)
    state_color_id = fields.Integer(string="ID Color", compute="_compute_color_html", store=False)
    show_icon = fields.Html(store=False)

    patient_name = fields.Char(string="Patient Name", compute="_compute_data", store=False)
    mobile = fields.Char(string="Teléfono", compute="_compute_data", store=False)
    # patient_state = fields.Char(string="Estado", compute="_compute_data", store=False)
    state_appointment = fields.Many2one(
        'appointment.state',
        string="Estado de la Cita",
        # default=lambda self: self.env['appointment.state'].search([('code', '=', 'confirmada')].id or 1, limit=1),
        help="Estado actual de la cita que se reflejará en la tarjeta."
    )
    description_plain = fields.Text(compute='_compute_data', string='Description (Plain Text)')

    # state_color = fields.Html(string="Color HTML")

    # region TODO: Campos que controlan multiples CALENDARIOS

    joint_calendar_id = fields.Many2one("joint.calendar.clodofy", string="Joint Calendar Clodofy", ondelete="cascade",
                                        index=True)

    # endregion

    bg_color = fields.Char(string="Color del fondo", compute="_compute_bg", store=False, default="#1E90FF")
    meeting_attendee_count = fields.Integer(string="Asistentes únicos", compute="_compute_attendee_count", store=False)

    @api.depends('state_appointment')
    def _compute_color_html(self):
        for rec in self:
            rec.state_color = rec.state_appointment.color or '#ffffff'
            rec.state_color_id = rec.state_appointment.id or -1
            rec.show_icon = '<i class="fa fa-check-circle me-2 fs-1"/>'

    @api.depends('patient_name', 'mobile', 'description_plain')
    def _compute_data(self):
        for rec in self:
            rec.patient_name = rec.attendee_ids[0].partner_id.name.upper() if rec.attendee_ids else ""
            rec.mobile = (
                    rec.attendee_ids[0].partner_id.mobile or rec.attendee_ids[0].phone) if rec.attendee_ids else ""
            # rec.description_plain = html2plaintext(rec.description) if rec.description else False
            rec.description_plain = html2plaintext(
                getattr(rec.attendee_ids[0].partner_id, 'patient_history', "") or "") if rec.attendee_ids else ""
            # rec.patient_state = rec.attendee_ids[0].state if rec.attendee_ids[0] else ""

    @api.depends('bg_color')
    def _compute_bg(self):
        for rec in self:

            rec.bg_color = rec.joint_calendar_id.bg_color if rec.joint_calendar_id else "#d1d1d1"
            if rec.categ_ids:
                if rec.categ_ids.filtered(lambda c: c.name.upper() == 'NUEVO'):
                    rec.bg_color = "#FFF0A3"

    @api.depends('attendee_ids.partner_id')
    def _compute_attendee_count(self):
        for rec in self:
            rec.meeting_attendee_count = len(rec.attendee_ids.mapped('partner_id'))

    # state_color = fields.Char(string="color de estado", compute='_compute_state_color')

    # @api.depends('state_appointment')
    # def _compute_state_color(self):
    # for rec in self:
    #     if rec.state_appointment == 'cancelada':
    #         rec.state_color = "background-color: black;"
    #     elif rec.state_appointment == 'lista_espera':
    #         rec.state_color = "background-color: orange;"
    #     elif rec.state_appointment == 'no_contesta':
    #         rec.state_color = "background-color: red;"
    #     elif rec.state_appointment == 'confirmada':
    #         rec.state_color = "background-color: green;"
    #     elif rec.state_appointment == 'avisar_cambio':
    #         rec.state_color = "background-color: yellow;"
    #     elif rec.state_appointment == 'en_consulta':
    #         rec.state_color = "background-color: blue;"
    #     elif rec.state_appointment == 'realizada':
    #         # Aquí, opcionalmente, podrías agregar un icono (check) en la vista
    #         rec.state_color = "background-color: green;"
    #     elif rec.state_appointment == 'urgente_vip':
    #         rec.state_color = "background-color: pink;"
    #     else:
    #         rec.state_color = ""
    # pass

    def action_open_whatsapp_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar WhatsApp',
            'res_model': 'calendar.whatsapp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_event_ids': [(6, 0, self.ids)]
            }
        }

    def action_open_attendee_partners(self):
        partners = self.mapped('attendee_ids.partner_id')
        if len(partners) == 1:
            # Si hay solo un contacto, ir directo al formulario
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'res_id': partners.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # Si hay varios, mostrar vista múltiple
            return {
                'name': 'Contactos asistentes',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'kanban,tree,form',
                'domain': [('id', 'in', partners.ids)],
                'context': {'create': False},
            }
