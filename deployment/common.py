"""
Module for general deployment tools and utils.
"""

import socket
from fabric import api as fabric_api
from lib.util import read_config


class DeploymentContext(object):
    """Provide necessary context to Fabric.

    Calss to read necessary information from a configuration file. The class
    then build context for Fabric to use. The class also takes a dict
    in the following format {"user":"UserName","key_filename":"Path"}.
    The idea is be able to overwrite the most necessary part of
    the configuration on the fly without the need to change the
    config file, etc/deployment.conf

    Attributes:
        config_file: string that represent the path to the config file.
        auth_info : dict that has {"user":"UserName","key_filename":"Path"}
        format.
    """

    def __init__(self, config_file=None, auth_info=None):
        """Inits DeploymentContext"""
        self.config_file = config_file
        self.auth_info = auth_info

    def create_context(self):
        """Create context for Fabric

        Create the necessary information for Fabric to work. If auth_info
        is provided then we ignore the information in the config file regarding
        the user and the key file. We will use what is provided instead.

        Args:
            none

        Return:
            fabric context or False

        """
        try:
            deployment_config = read_config(self.config_file)
            if self.auth_info:
                context = fabric_api.settings(
                    fabric_api.hide('running', 'stdout', 'stderr', 'warnings'),
                    user=self.auth_info['user'],
                    key_filename=[].append(self.auth_info['key_filename']),
                    disable_known_hosts=bool(deployment_config.get("fabric", "disable_known_hosts")),
                    linewise=bool(deployment_config.get("fabric", "linewise")),
                    warn_only=bool(deployment_config.get("fabric", "warn_only")),
                    abort_on_prompts=bool(deployment_config.get("fabric", "abort_on_prompts")),
                    always_use_pty=bool(deployment_config.get("fabric", "always_use_pty")),
                    timeout=int(deployment_config.get("fabric", "timeout"))
                )

            else:
                context = fabric_api.settings(

                    fabric_api.hide('running', 'stdout', 'stderr', 'warnings'),
                    user=deployment_config.get("fabric", "user"),
                    key_filename=[].append(deployment_config.get("fabric", "key_filename")),
                    disable_known_hosts=bool(deployment_config.get("fabric", "disable_known_hosts")),
                    linewise=bool(deployment_config.get("fabric", "linewise")),
                    warn_only=bool(deployment_config.get("fabric", "warn_only")),
                    abort_on_prompts=bool(deployment_config.get("fabric", "abort_on_prompts")),
                    always_use_pty=bool(deployment_config.get("fabric", "always_use_pty")),
                    timeout=int(deployment_config.get("fabric", "timeout"))
                )

        except:
            return False
        return context


def check_port_status(address, port=22, timeout=2):
    """Check weather a remote port is accepting connection.

    Given a port and an address, we establish a socket connection
    to determine the port state

    Args :
        address (string): address of the machine, ip or hostname
        port (int) : port number to connect to
        timeout (int) : time to wait for a response

    return :
        bool
            True: if port is accepting connection
            False : if port is not accepting

    """

    default_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((address, port))
    except:
        return False
    finally:
        remote_socket.close()
        socket.setdefaulttimeout(default_timeout)
    return True


def run_remote_command(address, command, config_file=None, auth_info=None):
    """Run a command in a remote machine.

    Given a machine address, a context and a command, the function uses fabric to execute the
    command in the remote machines.

    Args:
        address (string) : address of the machine
        context (Fabric.Context) : fabric context
        command ( string ) : command to execute

    Return:
        tuple (return code, stdout and stderr)
    """

    context = DeploymentContext(config_file, auth_info).create_context()
    if context:
        with context:
            fabric_api.env.host_string = address
            results = fabric_api.run(command)
        return results.succeeded, results.stdout, results.stderr
    else:
        return False, '', ''
