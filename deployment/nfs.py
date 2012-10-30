"""
Module to deploy debian NFS server and instruct debian clients to mount its export
Usage :

nfs_server = NfsServer("server_ip","../etc/deployment.conf")
status = nfs_server.run()
if status[0]:
    nfs_client = NfsClient("client_ip","../etc/deployment.conf","server_ip")
    status = nfs_client.run()
    if status[0]:
        print "win"

"""
from common import run_remote_command
from common import check_port_status
from lib import util


class NfsServer(object):
    """Class to deploy nfs server in a given debian machine.
    Attributes:
        hostname (string): hostname of the server we want to be nfs server
        config_file (string): path to the config file
        auth_info (dict) : dict that has {"user":"UserName","key_filename":"Path"} format
    """

    def __init__(self, hostname, config_file, auth_info=None):
        """Inits calss"""

        self.hostname = hostname
        self.config_file = config_file
        self.auth_info = auth_info
        self.config_obj = util.read_config(config_file)

    def check_requirements(self):
        """Check requirements for nfs deployment.

        Function that attempt to determine if the job will success beforehand.

        Args:
            none
        Retunrs:
            Bool
        """
        return {'alive': check_port_status(self.hostname)}

    def pre_pkg_install(self):
        """Commands to be executed before the packages are installed.

         Args:
            None
        Return:
            tuple : (status ( bool ), stdout (string) , stderr(string) )
        """
        result = run_remote_command(self.hostname, "apt-get update", self.config_file, self.auth_info)
        return result

    def install_pkgs(self):

        result_dict = {}
        packages_to_install = self.config_obj.get("nfs", "server_pkgs").split(",")
        command_to_run = 'DEBIAN_FRONTEND=noninteractive apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s'
        for pkg in packages_to_install:
            if pkg.strip():
                result = run_remote_command(self.hostname, command_to_run % pkg.strip(), self.config_file, self.auth_info)
                result_dict[pkg.strip()] = result
                if not result[0]:
                    break
        return result_dict

    def post_pkg_install(self):
        result_dict = {}
        dir_to_export = self.config_obj.get("nfs", "server_dir")
        export_options = self.config_obj.get("nfs", "export_options")
        services_to_restart = self.config_obj.get("nfs", "server_services").split(",")

        commands_to_execute = [
            "test -d %s || mkdir -p %s && chmod 777 %s" % (dir_to_export, dir_to_export, dir_to_export),
            'echo "%s %s" > /etc/exports' % (dir_to_export, export_options),
            "exportfs -av"]

        commands_to_execute.extend(["service %s restart" % service.strip() for service in services_to_restart])

        for command in commands_to_execute:
            result = run_remote_command(self.hostname, command, self.config_file, self.auth_info)
            result_dict[command] = result
            if not result[0]:
                break
        return result_dict

    def run(self):
        if self.check_requirements():
            if self.pre_pkg_install()[0]:
                results = self.install_pkgs()
                for key, value in results.iteritems():
                    if not value[0]:
                        return False, results

                results = self.post_pkg_install()
                for key, value in results.iteritems():
                    if not value[0]:
                        return False, results

                return True
            return False, "NfsServer failed in pre_pkg_install state"
        return False, "NfsServer failed in requirements check state "


class NfsClient(object):

    def __init__(self, hostname, config_file, server_address, auth_info=None):

        self.hostname = hostname
        self.config_file = config_file
        self.auth_info = auth_info
        self.config_obj = util.read_config(config_file)
        self.server_address = server_address

    def check_requirements(self):
        return {'alive': check_port_status(self.hostname)}

    def pre_pkg_install(self):
        result = run_remote_command(self.hostname, "apt-get update", self.config_file, self.auth_info)
        return result

    def install_pkgs(self):
        result_dict = {}
        packages_to_install = self.config_obj.get("nfs", "client_pkgs").split(",")
        command_to_run = 'DEBIAN_FRONTEND=noninteractive apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s'
        for pkg in packages_to_install:
            if pkg.strip():
                result = run_remote_command(self.hostname, command_to_run % pkg.strip(), self.config_file, self.auth_info)
                result_dict[pkg.strip()] = result
                if not result[0]:
                    break
        return result_dict

    def post_pkg_install(self):
        result_dict = {}
        exported_dir = self.config_obj.get("nfs", "server_dir")
        dir_to_mount = self.config_obj.get("nfs", "client_dir")
        mount_options = self.config_obj.get("nfs", "mount_options")
        print mount_options
        services_to_restart = self.config_obj.get("nfs", "client_services").split(",")

        commands_to_execute = [
            "test -d %s || mkdir -p %s" % (dir_to_mount, dir_to_mount),
            "%s %s:%s %s" % (mount_options, self.server_address, exported_dir, dir_to_mount)]

        print commands_to_execute

        commands_to_execute.extend(["service %s restart" % service.strip() for service in services_to_restart])

        for command in commands_to_execute:
            result = run_remote_command(self.hostname, command, self.config_file, self.auth_info)
            result_dict[command] = result
            if not result[0]:
                break
        return result_dict

    def run(self):
        if self.check_requirements():
            if self.pre_pkg_install()[0]:
                results = self.install_pkgs()
                for key, value in results.iteritems():
                    if not value[0]:
                        return False, results

                results = self.post_pkg_install()
                for key, value in results.iteritems():
                    if not value[0]:
                        return False, results

                return True
            return False, "NfsClient failed in pre_pkg_install state"
        return False, "NfsClient failed in requirements check state "
