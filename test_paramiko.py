import re
import time

import paramiko

from argparse_methods import argument_parser


class SshRequest:
    def __init__(self, hostname=None, username=None, password=None, port=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    def connector(self):
        self.client.connect(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port,
            look_for_keys=False,
            allow_agent=False)

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)

        while not stdout.channel.exit_status_ready():
            time.sleep(0.1)

        data_decode = stdout.read().decode("utf-8") + stderr.read().decode("utf-8")

        exit_status = stdout.channel.exit_status

        return data_decode, exit_status


def convert_to_int(lst):
    list_of_number = []
    for i in lst:
        try:
            list_of_number.append(int(i))
        except:
            pass
    return list_of_number


def print_res(to_print):
    if type(to_print) == list or type(to_print) == set:
        for p in to_print:
            print(p)
    else:
        print(to_print)

    print("-" * 30)


if __name__ == '__main__':
    def result(args_values):
        hname = args_values.ip.partition('@')[-1]
        uname = args_values.ip.partition('@')[:-2]
        password = args_values.password

        try:
            ssh_request_item = SshRequest(hname, *uname, password, args_values.p)
            ssh_request_item.connector()

            data_decode = ssh_request_item.execute_command("cat /etc/os-release")
            print_res(re.search(r'.*PRETTY_NAME=\"(.*)\"', data_decode[0]).groups()[0])

            # _________________________________________________________________________________________________________

            data_decode = ssh_request_item.execute_command("uname -r")
            print_res(data_decode[0])

            # _________________________________________________________________________________________________________

            data_decode = ssh_request_item.execute_command("ls /proc/")
            data_list = data_decode[0].split()
            converted_list = convert_to_int(data_list)
            to_print = []
            for j in converted_list:
                data_decode1, exit_status = ssh_request_item.execute_command("readlink -f /proc/" + str(j) + "/exe")
                if exit_status == 0:
                    to_print.append(data_decode1.replace("\n", ""))
            print_res(set(to_print))

            # _________________________________________________________________________________________________________
            data_decode = ssh_request_item.execute_command("cat /etc/passwd")
            data_list = data_decode[0].split()
            to_print = []
            for item in data_list:
                i = re.search(r"^(.*):[x].*(/bin/bash)$", item)
                if i is not None:
                    to_print.append("user= " + i.groups()[0])
            print_res(to_print)

            ssh_request_item.client.close()

        except Exception as err:
            print(f'Error occurred: {err}')


    result(argument_parser())
