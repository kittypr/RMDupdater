#!/usr/bin/env python3
import argparse
import os
import subprocess

from RMDupdater import check, mdparse


def check_token():
    command = 'RMD_updater_create_token.py'  # FIX THIS
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    answer = proc.communicate()


def write_changes_file(changed_code_ancestors, filename):
    filename += '.changes'
    with open(filename, 'w') as changes_file:
        changes_file.write(changed_code_ancestors)


def main(input_echo_md, gdoc_id, filename, fair, warnings=False):
    extractor = mdparse.TableExtractor(warnings)
    tables = extractor.parse(input_echo_md)
    fair_extractor = mdparse.TableExtractor(False)
    fair_tables = fair_extractor.parse(fair)
    result = check.run_local_comparison(tables, fair_tables)
    if result is None:  # some errors occurred
        return
    if len(result) == 0:
        print('UP TO DATE')
    else:
        print('OUTDATED BLOCKS FOUNDED')

    changed_code_ancestors = ''
    for index in tables.keys():
        if index[1] in result:
            changed_code_ancestors += '~~ CONTEXT\n' + index[0][0] + '\n~~ CHANGED BLOCK\n' + index[0][1] +\
                                          '\n~~ END\n'
    write_changes_file(changed_code_ancestors, filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RMDupdater checks tables from given MD doc and Gdoc, '
                                                 'finds differences, logs code that generates outdated information.')
    parser.add_argument('input', help='*.md file generated from *.rmd with "echo=TRUE"', action='store')
    parser.add_argument('gdoc_id', help='Gdoc id.', action='store')
    parser.add_argument('name', help='Name for unique changes filename', action='store')
    parser.add_argument('fair', help='actual fair version', action='store')
    args = parser.parse_args()
    gdoc_id = args.gdoc_id
    input_echo_md = args.input
    filename = args.name
    fair = args.fair
    main(input_echo_md, gdoc_id, filename, fair, warnings=False)

