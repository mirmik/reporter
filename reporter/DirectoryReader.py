#!/usr/bin/env python3

import os
import json


class Report:
    def __init__(self, success, message, report_path, program):
        if isinstance(success, str):
            success = success.lower() == 'true'
        self.success = success
        self.message = message
        self.report_path = report_path
        self.program_name = program

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
        data = self.read_dictionary()
        return Report(success=data['success'], message=data['message'], report_path=self.path, program=data['program'])


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
            reports.append(report_reader.read_report())
        return reports


class ReportsAnalyzer:
    def __init__(self, reports):
        self.reports = reports

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
        return f'Success: {success}/{total}\n' \
            f'Unsuccessful: {list_of_unsuccessful}'

    def list_of_unsuccessful(self):
        unsuccessful = []
        for report in self.reports:
            if not report.success:
                unsuccessful.append(report)
        return unsuccessful


if __name__ == '__main__':
    directory_reader = DirectoryReader('reports')
    reports = directory_reader.read_reports()
    analyzer = ReportsAnalyzer(reports)
    print(analyzer.metareport())
