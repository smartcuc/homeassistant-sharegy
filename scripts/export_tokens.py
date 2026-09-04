import os
import sys
import json

sys.path.insert(0, '/var/www/sharegy/live')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings.prod'

import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from devices.models import Home, Device

User = get_user_model()
users = User.objects.filter(email__startswith='stress_user_').order_by('id')
export = []

for u in users:
    home = u.homes.first()
    devs = Device.objects.filter(home=home)
    dev_list = []
    for d in devs:
        dev_list.append({
            'id': str(d.id),
            'identifier': d.identifier,
            'name': d.name,
            'role': d.config.role.key if d.config and d.config.role else 'consumer',
            'base_power': 100.0,
        })
    ref = RefreshToken.for_user(u)
    export.append({
        'user_id': str(u.id),
        'email': u.email,
        'username': u.username,
        'access_token': str(ref.access_token),
        'home_id': str(home.id) if home else '',
        'devices': dev_list,
    })

with open('/tmp/stress_test_tokens_200u_4000d.json', 'w') as f:
    json.dump({'num_users': len(export), 'users': export}, f, indent=2)

print(f'Successfully exported {len(export)} tokens to /tmp/stress_test_tokens_200u_4000d.json')
