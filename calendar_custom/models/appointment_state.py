from odoo import models, fields, api


class AppointmentState(models.Model):
    _name = 'appointment.state'
    _description = 'Estado de la Cita'
    _order = 'sequence asc'

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    color = fields.Char(string="Color", help="Color representativo del estado en formato hexadecimal (#RRGGBB)")
