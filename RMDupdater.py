import argparse
import subprocess

import check
import mdparse

parser = argparse.ArgumentParser(description='RMDupdater checks tables from given MD doc and Gdoc, '
                                             'finds differences, logs code that generates outdated information.')
parser.add_argument('input', help='Input file. Use Pandoc`s input formats.', action='store')
parser.add_argument('gdoc_id', help='Gdoc id.', action='store')
args = parser.parse_args()


def check_token():
    command = 'python create_token.py'
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()


def write_changes_file(changed_code_ancestors):
    with open('log.changes', 'w') as changes_file:
        changes_file.write(changed_code_ancestors)


def main():
    extractor = mdparse.TableExtractor()
    tables = extractor.parse(args.input)
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
    result = check.run_comparison(gdoc_id=args.gdoc_id, tables=tables_array)
    if result is None:
        return
    changed_code_ancestors = ''
    for index in tables.keys():
        if index[1] in result:
            changed_code_ancestors += '# CONTEXT\n' + index[0][0] + '\n# CHANGED BLOCK\n' + index[0][1] +\
                                          '\n# END\n'
    write_changes_file(changed_code_ancestors)


if __name__ == '__main__':
    main()
