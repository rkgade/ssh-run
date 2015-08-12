"""ssh-run command line interface"""

import os

import click

import ssh_run
import ssh_run.ssh


def parse_hosts(hostslist, hostsfile):
    hosts = []

    if hostslist:
        hosts.extend(hostslist)

    if hostsfile:
        hosts.extend(host.decode('utf-8').strip() for host in hostsfile)

    return hosts


@click.command()
@click.option(
    '--host', '-h', 'hosts_list', metavar='HOSTNAME', multiple=True,
    help='A single hostname. Can be used multiple times.')
@click.option(
    '--hosts', '-H', 'hosts_file', type=click.File('rb'),
    help='A file with one host per line.')
@click.option(
    '--dry-run', '-n', is_flag=True,
    help='Don\'t run any commands.')
@click.option(
    '--sudo', '-s', is_flag=True, default=False,
    help='Run the command using sudo.')
@click.option(
    '--sudo-password', '-S',
    help='Password for --sudo. Prompts if not set.')
@click.option(
    '--timeout', '-t', type=click.INT, default=300,
    help='Command timeout in seconds.')
@click.option(
    '--workspace', '-w', is_flag=True, default=False,
    help='Copy the current workspace to a remote host.')
@click.option(
    '--workspace-path', '-W',
    type=click.Path(exists=True), default=os.getcwd(),
    help='The directory to use as the workspace.')
@click.option(
    '--verbose/--no-verbose', '-v', default=False,
    help='Output commands before running them.')
@click.version_option(ssh_run.__version__, '--version', '-V')
@click.argument('command', nargs=-1, required=True)
def main(hosts_list, hosts_file, dry_run, timeout, sudo, sudo_password,
         workspace, workspace_path, verbose, command):

    # Prompt the user for a password to use with sudo.
    if sudo and not sudo_password:
        sudo_password = click.prompt(
            '[sudo] password for remote hosts', hide_input=True, err=True)

    # Create a runner with the settings used on every host.
    runner = ssh_run.ssh.SSHRun(
        dry_run=dry_run, sudo=sudo, sudo_password=sudo_password,
        timeout=timeout, verbose=verbose, workspace=workspace,
        workspace_path=workspace_path)

    # Run the command on each host.
    for host in parse_hosts(hosts_list, hosts_file):
        runner.run(host, command)