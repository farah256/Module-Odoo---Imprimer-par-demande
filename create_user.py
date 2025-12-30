#!/usr/bin/env python3
import sys
import os
sys.path.append('/usr/lib/python3/dist-packages')

import odoo

# Initialize
odoo.tools.config.parse_config(['-d', 'X3D'])
registry = odoo.registry(odoo.tools.config['db_name'])

with registry.cursor() as cr:
    from odoo.api import Environment
    env = Environment(cr, 1, {})  # SUPERUSER_ID = 1
    
    # Create user
    user = env['res.users'].create({
        'name': 'Super Admin',
        'login': 'superadmin',
        'password': 'superadmin',
        'groups_id': [(6, 0, [env.ref('base.group_system').id])]
    })
    print(f"Created user: {user.login}")
