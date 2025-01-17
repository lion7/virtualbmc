# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import configparser
import os
from unittest import mock


from shipmi import config
from shipmi.tests.unit import base

_CONFIG_FILE = '/foo/.shipmi/daemon.conf'


@mock.patch('shipmi.config.CONFIG_FILE', _CONFIG_FILE)
class ShIPMIConfigTestCase(base.TestCase):

    def setUp(self):
        super(ShIPMIConfigTestCase, self).setUp()
        self.shipmi_config = config.ShIPMIConfig()
        self.config_dict = {'default': {'show_passwords': 'true',
                                        'config_dir': '/foo/bar/1',
                                        'pid_file': '/foo/bar/2',
                                        'server_port': '12345',
                                        'server_spawn_wait': 3000,
                                        'server_response_timeout': 5000},
                            'log': {'debug': 'true', 'logfile': '/foo/bar/4'},
                            'ipmi': {'session_timeout': '30'}}

    @mock.patch.object(config.ShIPMIConfig, '_validate')
    @mock.patch.object(config.ShIPMIConfig, '_as_dict')
    @mock.patch.object(configparser, 'ConfigParser')
    def test_initialize(self, mock_configparser, mock__as_dict,
                        mock__validate):
        config = mock_configparser.return_value
        self.shipmi_config.initialize()

        config.read.assert_called_once_with(_CONFIG_FILE)
        mock__as_dict.assert_called_once_with(config)
        mock__validate.assert_called_once_with()

    @mock.patch.object(os.path, 'exists')
    def test__as_dict(self, mock_exists):
        mock_exists.side_effect = (False, True)
        config = mock.Mock()
        config.sections.side_effect = ['default', 'log', 'ipmi'],
        config.items.side_effect = [[('show_passwords', 'true'),
                                     ('config_dir', '/foo/bar/1'),
                                     ('pid_file', '/foo/bar/2'),
                                     ('server_port', '12345')],
                                    [('logfile', '/foo/bar/4'),
                                     ('debug', 'true')],
                                    [('session_timeout', '30')]]
        ret = self.shipmi_config._as_dict(config)
        self.assertEqual(self.config_dict, ret)

    def test_validate(self):
        self.shipmi_config._conf_dict = self.config_dict
        self.shipmi_config._validate()

        expected = self.config_dict.copy()
        expected['default']['show_passwords'] = True
        expected['default']['server_response_timeout'] = 5000
        expected['default']['server_spawn_wait'] = 3000
        expected['default']['server_port'] = 12345
        expected['log']['debug'] = True
        expected['ipmi']['session_timeout'] = 30
        self.assertEqual(expected, self.shipmi_config._conf_dict)
