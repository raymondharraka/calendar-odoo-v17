{
    'name': 'Calendar Custom',
    'version': '1.0',
    'summary': 'Customizations for the Calendar module in Odoo 17',
    'description': """
        Calendar Custom Module

        This module extends the calendar functionality in Odoo 17 by adding
        custom fields to calendar events and providing a custom menu and action.
    """,
    'category': 'Tools',
    'author': 'Your Name',
    'website': 'http://www.example.com',
    'license': 'LGPL-3',
    'depends': ['base', 'calendar', 'web','whatsapp', 'web_calendar_base_mac5', 'calendar_resource_assignee_mac5'],
    'data': [
        'security/calendar_custom_security.xml',
        'security/ir.model.access.csv',

        'wizard/calendar_whatsapp.xml',
        'data/appointment_state_data.xml',
        'data/calendar_event_type_data.xml',
        'views/appointment_state.xml',
        'views/calendar_custom_views.xml',
        'views/joint_calendar_clodofy.xml',
        'views/res_users.xml',
        'views/calendar_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "calendar_custom/static/src/xml/attendee_calendar_common_renderer_inherit.xml",
            'calendar_custom/static/src/css/calendar_override.css',
        ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
