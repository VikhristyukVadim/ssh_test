import re

import paramiko

from argparse_methods import argument_parser

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

request_commands = [
    {"OS_name": ["cat /etc/os-release", "PRETTY_NAME="]},
    {"kernel_version": ["uname -r", None]},
    {"process_list": ["ls /proc/", None]},
    {"users_list": ["cat /etc/passwd", None]}
]


# pwdx - путь к процессу
# ls -l /proc/14193/exe


class SshRequest:
    def __init__(self, hostname=None, username=None, password=None, port=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

    def connector(self):
        client.connect(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port,
            timeout=5,
            look_for_keys=False,
            allow_agent=False)


def convert_to_int(lst):
    list_of_number = []
    for i in lst:
        try:
            list_of_number.append(int(i))
        except:
            pass
    return list_of_number


if __name__ == '__main__':
    def result(args_values):
        hname = args_values.ip.partition('@')[-1]
        uname = args_values.ip.partition('@')[:-2]
        password = args_values.password

        try:
            SshRequest(hname, *uname, password, args_values.p).connector()

            for i in request_commands:
                command_name = i.keys()
                command = i.get(*command_name)

                stdin, stdout, stderr = client.exec_command(command[0])
                data_decode = stdout.read().decode("utf-8") + stderr.read().decode("utf-8")

                search_string = command[1] if len(command) > 1 else None
                data_list = data_decode.split()

                to_print = []

                if search_string is not None:
                    to_print = re.search(r'.*PRETTY_NAME=\"(.*)\"', data_decode).groups()[0]

                elif ''.join(command_name) == 'process_list':
                    converted_list = convert_to_int(data_list)
                    for j in converted_list:
                        # print('j--------------------->>>>',j)
                        stdin, stdout, stderr = client.exec_command("readlink -f /proc/" + str(j) + "/exe")

                        data_decode = stdout.read().decode("utf-8") + stderr.read().decode("utf-8")
                        exit_status = stdout.channel.exit_status
                        exit_status_ready = stdout.channel.exit_status_ready()

                        if exit_status_ready:
                            if exit_status == 0:
                                to_print.append(data_decode.replace("\n", ""))

                elif ''.join(command_name) == 'users_list':
                    for item in data_list:
                        i = re.search(r"^(.*):[x].*(/bin/bash)$", item)
                        if i is not None:
                            to_print.append("user= " + i.groups()[0])
                else:
                    to_print = data_decode

                print("result of  OS(" + str(*uname) + ") and  command " +
                      "(" + str(*command_name) + "): ")

                if type(to_print) == list:
                    for p in to_print:
                        print(p)
                else:
                    print(to_print)

                print("-" * 30)

            client.close()

        except Exception as err:
            print(f'Error occurred: {err}')


    result(argument_parser())
