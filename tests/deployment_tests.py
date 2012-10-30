"""
Module that tests various deployment functionality
"""

import unittest
from deployment import common

class test_deployment_common(unittest.TestCase):


    def setUp(self):
        self.testing_machine = "vm-148-116.uc.futuregrid.org"
        self.bad_machine_name = "Idonotexistwallah.wrong"
        self.key_filename = "/Users/ali/.ssh/ali_alzabarah_fg.priv"

    def test_port_status_check(self):
        self.assertFalse(common.check_port_status("google.com"))
        self.assertTrue(common.check_port_status("research.cs.colorado.edu"))
        self.assertTrue(common.check_port_status("google.com",80,2))
        self.assertFalse(common.check_port_status("Idonotexistwallah.wrong"))
        self.assertFalse(common.check_port_status("256.256.256.256"))

    def test_deployment_context(self):
        deployment_context = common.DeploymentContext("../etc/deployment.conf")
        self.assertIsNotNone(deployment_context.create_context())

    def test_run_remote_command(self):
        result, stdout, stderr = common.run_remote_command(self.testing_machine,
            "grep ewrqwerasdfqewr /etc/passwd", "../etc/deployment.conf")
        self.assertFalse(result)
        result, stdout, stderr = common.run_remote_command(self.testing_machine,
            "uname -a", "../etc/deployment.conf", {"user":"root","key_filename":self.key_filename})
        self.assertTrue(result)



if __name__ == '__main__':
    unittest.main()
