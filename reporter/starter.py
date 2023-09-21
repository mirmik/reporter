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
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--save-output', action='store_true')
    parsed = parser.parse_args(starter_args[1:])

    stdout, stderr, returncode = start_application_and_read_output_and_status(
        progargs)

    status = True if returncode == 0 else False
    message = "Success" if status else "Failure"
    progname = progargs[0]

    print("Reporter starts with arguments:")
    print(f"\tPath: {parsed.path}")

    print("Final report:")

    dct = {
        "success": status,
        "message": message,
        "program": progname
    }
    if parsed.save_output:
        dct['stdout'] = stdout
        dct['stderr'] = stderr

    print_report_to_console(dct)

    report_path = report_path(dct, parsed.path)
    print(f"Report path: {report_path}")
    print_report_to_file(dct, report_path)
