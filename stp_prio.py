#!/usr/bin/env python3

import os
import sys
import requests
import argparse

DEFAULT_HOST = 'unifi-controller-url:8443'
DEFAULT_USER = 'admin'
DEFAULT_PASS = 'hunter2'
DEFAULT_SITE = 'abcdwxyz'

class Unifi:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf = ''

    def login(self):
        payload = {'username': self.username, 'password': self.password}
        r = self.request('/api/login', payload)
        if not r.ok:
            print(f'Login failed at {self.host}/api/login: {r.text}', file=sys.stderr)
        return r.ok

    def request(self, path, data=None, method='POST'):
        if data is None:
            data = {}
        method = method.lower()
        if method not in ['get', 'post', 'put', 'delete']:
            raise ValueError(f'Unsupported HTTP method: {method}')
        uri = f'https://{self.host}{path}'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.csrf:
            headers['X-CSRF-Token'] = self.csrf
        r = getattr(self.session, method)(
            uri, json=data, verify=True, headers=headers
        )
        self.csrf = r.headers.get('X-CSRF-Token', self.csrf)
        return r

def validate_response(res) -> bool:
    try:
        response_data = res.json()
        if res.status_code == 200 and response_data.get('meta', {}).get('rc') == 'ok':
            return True
    except ValueError:
        pass
    print(f'Error while accessing {res.url}: {res.text}', file=sys.stderr)
    return False

def get_values(device, keys, default='-'):
    return [device.get(key, default) for key in keys]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False,
        description='Show Unifi switch STP priority')
    parser.add_argument('--help','-h',
        action='help',
        help=argparse.SUPPRESS)
    parser.add_argument('--site','-s',
        default=DEFAULT_SITE,
        help='Site ID (as shown in Unifi web interface)')
    args = parser.parse_args()

    SITE = args.site.lower() if args.site else DEFAULT_SITE
    HOST = os.getenv('UNIFI_HOST', DEFAULT_HOST)
    USER = os.getenv('UNIFI_USER', DEFAULT_USER)
    PASS = os.getenv('UNIFI_PASS', DEFAULT_PASS)

    sess = Unifi(host=HOST, username=USER, password=PASS)
    try:
        if not sess.login():
            exit(2)
    except Exception as e:
        print(e, file=sys.stderr)
        exit(1)

    res = sess.request(f'/api/s/{SITE}/stat/device', method='get')
    if not validate_response(res):
        exit(1)
    switches = [dev for dev in res.json().get('data') if dev.get('type') == 'usw']
    keys = ['name', 'stp_priority', 'stp_version', 'shortname', 'mac', 'ip', 'version']
    headers = ['device_name', 'prio', 'type', 'model', 'MAC', 'IP', 'fw_version']
    rows = [headers]
    for s in sorted(switches, key=lambda x: int(x['stp_priority']), reverse=False):
        rows.append(get_values(s, keys))
    col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(headers))]
    col_widths = [width + 2 for width in col_widths]
    header_line = ''.join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
    data_lines = [
        ''.join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        for row in rows[1:]
    ]

    print(header_line)
    print('─' * len(header_line))
    print('\n'.join(data_lines))
