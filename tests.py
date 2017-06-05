import socket
import unittest
from pprint import pprint

from mock import patch
from pyassert import *

from assets.lvs_commands_datas import lvs_asset
from nrlvmd import parse_config_file, set_environment_variables, set_headers, set_datas


class NrLvmTests(unittest.TestCase):

    def tearDown(self):
        if "NEWRELIC_LICENCE_KEY" in os.environ:
            del os.environ["NEWRELIC_LICENCE_KEY"]
        if "NEWRELIC_HOSTNAME" in os.environ:
            del os.environ["NEWRELIC_HOSTNAME"]

    def _set_environment_variable(self):
        config_values = {"license_key": "test_licence_key", "hostname": "test_hostname", }
        set_environment_variables(config_values)

    def test_parse_config_file(self):
        config_values = parse_config_file("./assets/nr_config_file.cfg")
        assert_that(config_values["hostname"]).equals("test_hostname")
        assert_that(config_values["license_key"]).equals("test_licence_key")

    def test_parse_config_without_hostname(self):
        config_values = parse_config_file("./assets/nr_config_without_hostname.cfg")
        assert_that(config_values["license_key"]).equals("test_licence_key")
        assert_that(config_values).does_not_contain("hostname")

    def test_set_environment_from_config_file(self):
        config_values = {"hostname": "test_hostname", "license_key": "test_licence_key"}
        set_environment_variables(config_values)
        assert_that(os.environ["NEWRELIC_LICENCE_KEY"]).equals("test_licence_key")
        assert_that(os.environ["NEWRELIC_HOSTNAME"]).equals("test_hostname")

    def test_set_environment_from_config_file_without_hostname(self):
        config_values = {"license_key": "test_licence_key"}
        set_environment_variables(config_values)
        assert_that(os.environ["NEWRELIC_LICENCE_KEY"]).equals("test_licence_key")
        assert_that(os.environ["NEWRELIC_HOSTNAME"]).equals(socket.gethostname())

    def test_do_not_override_environment_variable(self):
        os.environ["NEWRELIC_LICENCE_KEY"] = "initial_licence"
        os.environ["NEWRELIC_HOSTNAME"] = "initial_hostname"
        config_values = {"license_key": "test_licence_key", "hostname": "test_hostname",}
        set_environment_variables(config_values)
        assert_that(os.environ["NEWRELIC_LICENCE_KEY"]).equals("initial_licence")
        assert_that(os.environ["NEWRELIC_HOSTNAME"]).equals("initial_hostname")

    def test_set_headers_from_environment_variable(self):
        self._set_environment_variable()
        header = set_headers()
        assert_that(header['X-License-Key']).equals("test_licence_key")

    def test_set_headers_without_environment_variable(self):
        header = set_headers()
        assert_that(header['X-License-Key']).equals(None)

    @patch("nrlvmd.subprocess.check_output")
    def test_set_datas_from_lvs_command(self, mock_check_output):
        self._set_environment_variable()
        check_output = "test_thinpool,38,12,2"
        mock_check_output.return_value = check_output.encode('utf8')
        datas = set_datas()
        assert_that(datas[0]['components'][0]["metrics"]).contains('Component/lvm/usage/test_thinpool/Data/Used[percent]')
        assert_that(datas[0]['components'][0]["metrics"]).contains('Component/lvm/usage/test_thinpool/Metadata/Used[percent]')
        assert_that(datas[0]['components'][0]["metrics"]['Component/lvm/usage/test_thinpool/Data/Used[percent]']).equals(float(12))
        assert_that(datas[0]['components'][0]["metrics"]['Component/lvm/usage/test_thinpool/Metadata/Used[percent]']).equals(float(2))

    def test_set_datas_failed_if_lvs_is_not_installed(self):
        def test_set_data():
            datas = set_datas()
            return datas

        self._set_environment_variable()
        assert_that(test_set_data).raises(OSError)

    @patch("nrlvmd.subprocess.check_output")
    def test_set_datas_from_wrong_lvs_returned_values(self, mock_check_output):
        self._set_environment_variable()
        mock_check_output.return_value = "wrong_return"
        datas = set_datas()
        assert_that(datas).equals([])

    @patch("nrlvmd.subprocess.check_output")
    def test_set_datas_from_multiple_volumes(self, mock_check_output):
        self._set_environment_variable()
        check_output = lvs_asset
        mock_check_output.return_value = check_output.encode('utf8')
        datas = set_datas()
        assert_that(len(datas)).equals(8)

if __name__ == '__main__':
    unittest.main()