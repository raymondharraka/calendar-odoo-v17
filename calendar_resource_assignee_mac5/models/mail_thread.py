from lxml import etree

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(MailThread, self).get_view(view_id=view_id, view_type=view_type, **options)

        # if view_type == 'calendar' and options.get('action_id') == self.env.ref('calendar_resource_assignee_mac5.action_calendar_event_by_assignee').id:
        action_ids = self.env['ir.actions.act_window'].search([
            ('res_model', '=', 'calendar.event'),
            ('type', '=', 'ir.actions.act_window'),
            ('domain', 'ilike', 'joint_calendar_id'),
            ('context', 'ilike', 'resource_by_assignee'),
        ], order='id desc').ids
        action_ids.append(
            self.env.ref('calendar_resource_assignee_mac5.action_calendar_event_by_assignee').id
        )
        # if view_type == 'calendar' and options.get('action_id') in (self.env.ref('calendar_resource_assignee_mac5.action_calendar_event_by_assignee').id,self.env.ref('calendar_custom.action_calendar_event_by_assignee_chatgpt').id):
        if view_type == 'calendar' and options.get('action_id') in (action_ids):
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//calendar"):
                node.set('resource_by_assignee', 'resource_by_assignee')
                node.set('resource_type', 'timegrid')
            result['arch'] = etree.tostring(doc)
        return result
