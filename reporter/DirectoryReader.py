#!/usr/bin/env python3

import os
import json
import datetime
import shutil
import argparse


def parse_timestamp(timestamp):
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")


class Report:
    def __init__(self, success, message, report_path, program, timestamp):
        if isinstance(success, str):
            success = success.lower() == 'true'
        self.success = success
        self.message = message
        self.report_path = report_path
        self.program_name = program
        self.timestamp = parse_timestamp(timestamp)

    def __str__(self):
        return f'{self.program_name}: {self.success}'

    def __repr__(self):
        return f'{self.program_name}: {self.success}'


class ReportFileReader:
    def __init__(self, file_path):
        self.path = file_path

    def read_dictionary(self):
        with open(self.path, 'r') as f:
            s = f.read()
            data = json.loads(s)
        return data

    def is_success(self):
        data = self.read_dictionary()
        return data['success']

    def read_report(self):
        try:
            data = self.read_dictionary()
            return Report(success=data['success'], message=data['message'], report_path=self.path, program=data['program'], timestamp=data['timestamp'])
        except:
            print(f'Error while reading report from {self.path}')
            raise


class DirectoryReader:
    def __init__(self, directory_path):
        self.path = directory_path

    def files_list(self):
        files = os.listdir(self.path)
        return files

    def read_reports(self):
        files = self.files_list()
        reports = []
        for file in files:
            file_path = os.path.join(self.path, file)
            report_reader = ReportFileReader(file_path)
            try:
                reports.append(report_reader.read_report())
            except:
                continue
        return reports

    def read_last_delta_reports_by_timestamp(self, delta):
        reports = self.read_reports()
        last_day_reports = []
        for report in reports:
            if report.timestamp > datetime.datetime.now() - delta:
                last_day_reports.append(report)
        return last_day_reports

    def mtime_to_datetime(self, mtime):
        return datetime.datetime.fromtimestamp(mtime)

    def read_last_delta_reports_by_mtime(self, delta):
        errored = []
        files = self.files_list()
        reports = []
        for file in files:
            try:
                file_path = os.path.join(self.path, file)
                mtime = os.path.getmtime(file_path)
                if self.mtime_to_datetime(mtime) > datetime.datetime.now() - delta:
                    report_reader = ReportFileReader(file_path)
                    reports.append(report_reader.read_report())
            except:
                errored.append(file)
                continue
        return reports, errored


def read_config(path):
    with open(path, 'r') as f:
        s = f.read()
        data = json.loads(s)
    return data


class ReportsAnalyzer:
    def __init__(self, reports, errored):
        self.reports = reports
        self.errored = errored

    def count_success(self):
        success = 0
        for report in self.reports:
            if report.success:
                success += 1
        return success

    def metareport(self):
        success = self.count_success()
        total = len(self.reports)
        list_of_unsuccessful = self.list_of_unsuccessful()
        list_of_successful = [
            report for report in self.reports if report.success]
        return f'Success: {success}/{total}\n' \
            f'Unsuccessful: {[prog.program_name for prog in list_of_unsuccessful]}\n' \
            f'Successful: {[prog.program_name for prog in list_of_successful]}\n' \
            f'Errored: {self.errored}'

    def list_of_unsuccessful(self):
        unsuccessful = []
        for report in self.reports:
            if not report.success:
                unsuccessful.append(report)
        return unsuccessful


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str)
    parser.add_argument('--last-days', type=int, required=False)
    parser.add_argument('--last-hours', type=int, required=False)
    parser.add_argument('--last-minutes', type=int, required=False)
    parser.add_argument('--sanitize-errored', action='store_true')
    args = parser.parse_args()

    config_path = "/etc/reporter/config.json"
    print("Config path:", config_path)
    config = read_config(config_path)

    if not args.path:
        path = config['default_directory_path']

    if not os.path.exists(path):
        # make directory
        print(f'Creating directory {path}')
        os.makedirs(path)

    if args.last_days:
        timedelta = datetime.timedelta(days=args.last_days)
    elif args.last_hours:
        timedelta = datetime.timedelta(hours=args.last_hours)
    elif args.last_minutes:
        timedelta = datetime.timedelta(minutes=args.last_minutes)
    else:
        timedelta = datetime.timedelta(days=1)

    directory_reader = DirectoryReader(path)
    reports, errored = directory_reader.read_last_delta_reports_by_mtime(
        timedelta)
    analyzer = ReportsAnalyzer(reports, errored)
    print(analyzer.metareport())

    if args.sanitize_errored:
        print('Sanitizing errored...')
        # delete errored
        for file in errored:
            file_path = os.path.join(path, file)
            os.remove(file_path)
        print('Done')
