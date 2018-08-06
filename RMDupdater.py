import argparse
import check
import mdparse

parser = argparse.ArgumentParser(description='RMDupdater checks tables from given MD doc and Gdoc '
                                             'and finds differences.')
parser.add_argument('input', help='Input file. Use Pandoc`s input formats.', action='store')
parser.add_argument('gdoc_id', help='Gdoc id.', action='store')
args = parser.parse_args()

point = {'t': 'Para', 'c': [{'t': 'Str', 'c': '***WAS_CHANGED/REPLACED/REMOVED***'}]}


def write_changes_file(changed_code_ancestors):
    with open('log.changes', 'w') as changes_file:
        changes_file.write(changed_code_ancestors)


def main():
    extractor = mdparse.TableExtractor()
    tables = extractor.parse(args.input)
    tables_array = list()  # this array will be sent to apps script api
    for index in tables.keys():  # creating array with
        table = tables[index]
        header_row = table[0]
        has_content = False
        for cell in header_row:
            if cell != '':
                has_content = True
        if not has_content:
            table.pop(0)
        tables_array.append(table)
    result = check.run_comparison(gdoc_id=args.gdoc_id, tables=tables_array)
    changed_code_ancestors = ''
    if result:
        for index in tables.keys():
            if index[1] in result:
                changed_code_ancestors = index[0] + '/n #'
    write_changes_file(changed_code_ancestors)


if __name__ == '__main__':
    main()
