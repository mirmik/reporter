#!/usr/bin/env python3

import subprocess
import sys
import pprint
import argparse
import datetime
import os
import json


def start_application_and_read_output_and_status(args):
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8'), process.returncode


def print_report_to_console(report):
    pretty = pprint.PrettyPrinter(width=30)
    pretty.pprint(dct)


def read_config(path):
    with open(path, 'r') as f:
        s = f.read()
        data = json.loads(s)
    return data


def report_path(report, directory_path):
    progname = report['program']
    # progname must be a word started with a letter and consist of letters and digits
    progname = ''.join([c for c in progname if c.isalnum()])
    dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'{progname}_{dt}.report'
    path = os.path.join(directory_path, filename)
    return path


def print_report_to_file(report, path):
    with open(path, 'w') as f:
        json.dump(report, f, indent=4)


if __name__ == "__main__":
    index_of_minuses = sys.argv.index('--')
    progargs = sys.argv[index_of_minuses+1:]
    starter_args = sys.argv[:index_of_minuses]

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str)
    parser.add_argument('--save-output', action='store_true')
    parsed = parser.parse_args(starter_args[1:])

    config_path = "/etc/reporter/config.json"
    print("Config path:", config_path)
    config = read_config(config_path)

    if not parsed.path:
        path = config['default_directory_path']

    stdout, stderr, returncode = start_application_and_read_output_and_status(
        progargs)

    status = True if returncode == 0 else False
    message = "Success" if status else "Failure"
    progname = progargs[0]

    print("Reporter starts with arguments:")
    print(f"\tPath: {path}")

    print("Final report:")

    dct = {
        "success": status,
        "message": message,
        "program": progname,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "owner": os.environ.get('USER')
    }
    if parsed.save_output:
        dct['stdout'] = stdout
        dct['stderr'] = stderr

    print_report_to_console(dct)

    report_path = report_path(dct, path)
    print(f"Report path: {report_path}")
    print_report_to_file(dct, report_path)
