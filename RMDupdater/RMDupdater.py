import argparse
import os
import subprocess

import check, mdparse


def check_token():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    command = 'python ' + dir_path + '\create_token.py'
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    answer = proc.communicate()
    print(answer)


def write_changes_file(changed_code_ancestors):
    with open('log.changes', 'w') as changes_file:
        changes_file.write(changed_code_ancestors)


def main(input_echo_md, gdoc_id):
    extractor = mdparse.TableExtractor()
    tables = extractor.parse(input_echo_md)
    if tables is None:
        return
    tables_array = list()  # this array will be sent to apps script api
    for index in tables.keys():  # creating array with tables and indexes, deleting empty headers.
        table = tables[index]
        header_row = table[0]
        has_content = False
        for cell in header_row:
            if cell != '':
                has_content = True
        if not has_content:
            table.pop(0)
        tables_array.append(table)
    check_token()
    result = check.run_comparison(gdoc_id=gdoc_id, tables=tables_array)
    if result is None:
        return
    changed_code_ancestors = ''
    for index in tables.keys():
        if index[1] in result:
            changed_code_ancestors += '# CONTEXT\n' + index[0][0] + '\n# CHANGED BLOCK\n' + index[0][1] +\
                                          '\n# END\n'
    write_changes_file(changed_code_ancestors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RMDupdater checks tables from given MD doc and Gdoc, '
                                                 'finds differences, logs code that generates outdated information.')
    parser.add_argument('input', help='*.md file generated from *.rmd with "echo=TRUE"', action='store')
    parser.add_argument('gdoc_id', help='Gdoc id.', action='store')
    args = parser.parse_args()
    gdoc_id = args.gdoc_id
    input_echo_md = args.input
    main(input_echo_md, gdoc_id)