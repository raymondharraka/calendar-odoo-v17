from odoo import models, fields, api
from ast import literal_eval


class CalendarWhatsAppWizard(models.TransientModel):
    _name = 'calendar.whatsapp.wizard'
    _description = 'Asistente para envío de WhatsApp'

    # @api.model
    # def default_get(self, fields):
    #     result = super(CalendarWhatsAppWizard, self).default_get(fields)
    #
    #     # result['res_model'] = result.get('res_model') or self.env.context.get('active_model')
    #     #
    #     # active_ids = self.env.context.get('default_event_ids') or self.env.context.get('active_ids')
    #     active_ids = self.env.context.get('active_ids')
    #     if active_ids:
    #         # result['event_ids'] = active_ids
    #         result['recipient_count'] = len(active_ids)
    #     # if not result.get('res_id'):
    #     #     if not result.get('res_ids') and self.env.context.get('active_id'):
    #     #         result['res_id'] = self.env.context.get('active_id')
    #
    #     return result

    event_ids = fields.Many2many('calendar.event', string="Eventos")
    template_id = fields.Many2one('whatsapp.template', string="Plantilla de WhatsApp", required=True)
    preview_whatsapp = fields.Html(compute="_compute_preview_whatsapp", string="Message Preview")
    res_model = fields.Char('Document Model Name', store=False)
    # recipient_count = fields.Integer(string="Total de destinatarios", precompute=True,compute="_compute_recipient_count")
    recipient_count = fields.Integer(string="Total de destinatarios", compute="_compute_recipient_count")
    participant_ids = fields.Many2many('res.partner', string="Participantes", compute="_compute_participants",
                                       store=False)
    # free texts
    number_of_free_text = fields.Integer(string="Number of free text", compute='_compute_number_of_free_text')
    header_text_1 = fields.Char(string="Header Free Text", compute='_compute_free_text', store=True)

    @api.depends('event_ids', 'res_model')
    @api.depends_context('event_ids')
    def _compute_recipient_count(self):
        for wizard in self:
            recipients = wizard.event_ids.mapped('partner_ids')
            wizard.recipient_count = len(recipients)
            wizard.res_model = self.env.context['active_model']

    @api.depends('event_ids')
    def _compute_participants(self):
        for wizard in self:
            wizard.participant_ids = wizard.event_ids.mapped('partner_ids')

    def action_send_whatsapp(self):
        WhatsAppMessage = self.env['whatsapp.composer']

        for wizard in self:
            # for partner in wizard.participant_ids:

            for partner in wizard.event_ids:
                if not partner.mobile:
                    continue  # Evita errores si no tiene número

                # Se usa el partner como 'record' para la plantilla
                # vals = wizard.template_id._get_send_template_vals(partner, free_text_json={})
                vals = {
                    'phone': partner.mobile,
                    'wa_template_id': wizard.template_id.id,
                    'res_model': wizard.res_model or partner.__class__.__name__
                }
                if vals:
                    msg = WhatsAppMessage.with_context({'active_id': partner.id}).create(vals)
                    # msg._send()  # Enviar directamente (no esperar cron)
                    msg._send_whatsapp_template(force_send_by_cron=True)  # Enviar directamente (no esperar cron)
        return {'type': 'ir.actions.act_window_close'}

    @api.depends(lambda self: self._get_free_text_fields())
    def _compute_preview_whatsapp(self):
        """This method is used to compute the preview of the whatsapp message."""
        for record in self:
            rec = record._get_active_records()
            if record.template_id and rec:
                record.preview_whatsapp = self.env['ir.qweb']._render('whatsapp.template_message_preview', {
                    'body': record._get_html_preview_whatsapp(rec=rec[0]),
                    'buttons': record.template_id.button_ids,
                    'header_type': record.template_id.header_type,
                    'footer_text': record.template_id.footer_text,
                    'language_direction': 'rtl' if record.template_id.lang_code in ('ar', 'he', 'fa',
                                                                                    'ur') else 'ltr',
                })
            else:
                record.preview_whatsapp = None

    def _get_html_preview_whatsapp(self, rec):
        """This method is used to get the html preview of the whatsapp message."""
        self.ensure_one()
        template_variables_value = self.template_id.variable_ids._get_variables_value(rec)
        text_vars = self.template_id.variable_ids.filtered(lambda var: var.field_type == 'free_text')
        for var_index, body_text_var in zip(range(1, self.number_of_free_text + 1),
                                            text_vars.filtered(lambda var: var.line_type == 'body')):
            free_text_x = self[f'free_text_{var_index}']
            if free_text_x:
                template_variables_value[f'body-{body_text_var.name}'] = free_text_x
        if self.header_text_1 and text_vars.filtered(lambda var: var.line_type == 'header'):
            template_variables_value['header-{{1}}'] = self.header_text_1
        return self.template_id._get_formatted_body(variable_values=template_variables_value)

    # ------------------------------------------------------------
    # TOOLS
    # ------------------------------------------------------------
    @api.depends('template_id')
    def _compute_free_text(self):
        for rec in self:
            if rec.template_id.header_type == 'text':
                header_params = rec.template_id.variable_ids.filtered(lambda line: line.line_type == 'header')
                if rec.template_id.variable_ids and header_params:
                    header_param = header_params[0]
                    if header_param.field_type == 'free_text' and not rec.header_text_1:
                        rec.header_text_1 = header_param.demo_value
            if rec.template_id.variable_ids:
                free_text_count = 1
                for param in rec.template_id.variable_ids.filtered(
                        lambda line: line.line_type == 'body' and line.field_type == 'free_text'):
                    # This is just a hack to work on stable version as we can't force view update on stable.
                    # As we need to change view, it will be done properly on master.
                    if not rec._origin[f"free_text_{free_text_count}"]:
                        rec[f"free_text_{free_text_count}"] = param.demo_value
                    free_text_count += 1

    @api.depends('template_id')
    def _compute_number_of_free_text(self):
        for rec in self:
            if rec.template_id:
                rec.number_of_free_text = len(rec.template_id.variable_ids.filtered(
                    lambda line: line.field_type == 'free_text' and line.line_type == 'body'))
            else:
                rec.number_of_free_text = 0

    def _get_free_text_fields(self):
        return ["template_id"]

    def _get_active_records(self):
        self.ensure_one()
        return self.env[self.res_model].browse(self.event_ids[0].ids if self.event_ids else False)
