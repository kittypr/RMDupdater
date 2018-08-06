import json
import subprocess

from copy import copy

TABLE = ('Table', )
CODE = ('Code', 'CodeBlock')
BLOCK = ('Div', 'Header', 'Span')


class TableExtractor:

    def __init__(self):
        self.string_to_write = ''
        self.tables = dict()
        self.ancestor = ''
        self.content = ''

    def get_content(self):
        content = copy(self.content)
        self.content = ''
        return content

    def add_content(self, addition):
        self.content = self.content + addition

    def write_code(self, code):
        """Write to output file code elements.
        Since, element with title 'Code' or 'CodeBlock' has special structure of 'c'(Content) field, that looks like:
        [[0], 'code']
        where:
            [0] - list of attributes: identifier, classes, key-value pairs.
            'code' - string with code.
        we should parse it especially.
        Args:
            code - element with title 'Code' or 'CodeBlock'.
        """
        self.ancestor = code['c'][1]

    def write_special_block(self, block):
        con = 1
        if block['t'] == 'Header':
            con = 2
        self.list_parse(block['c'][con], without_write=True)

    def write_table(self, tab):
        """Write to output file table elements.
        This function is called every time, we meet 'Table' dictionary's title.
        Firstly, if we have some information in 'string_to_write' we record it, because we'll use this
        variable to collect information from table's cells.
        Table in pandoc's json has following structure:
        dict: { 't': 'Table'
                'c': [ [0] [1] [2] [3] [4] ]
              }
        Where:
        [0] - caption.
        [1] - is list of aligns by columns, looks like: [ { t: 'AlignDefault' }, ... ].
        [2] - widths of columns.
        [3] - is list of table's headers (top cell of every column), can be empty.
        [4] - list of rows, and row is list of cells.
        Since every cell's structure is the same as text's one, we just parse them as list and write one by one.
        Args:
            tab - dictionary with 't': 'Table".
        """

        table = list()
        row = list()
        headers = tab['c'][3]
        if headers:
            for col in headers:
                self.list_parse(col, without_write=True)
                cell_content = self.get_content()
                row.append(cell_content)
            table.append(row)
        t_content = tab['c'][4]
        for line in t_content:
            row = list()
            for col in line:
                self.list_parse(col, without_write=True)
                cell_content = self.get_content()
                row.append(cell_content)
            table.append(row)
        self.tables[(self.ancestor, len(self.tables))] = table

    def dict_parse(self, dictionary, without_write=False):
        """Parse dictionaries.
        Dictionary represents some json-object. The kind of json object depends on its 't' (title) field.
        We will parse it differently depending on different titles.

        Args:
            dictionary - object with 't' and sometimes 'c' fields.
            without_write - indicate inside/outside table TODO: CHANGE VARIABLE NAME
        """

        try:
            if dictionary['t'] in TABLE:  # blocks that may have content
                self.write_table(dictionary)
            elif dictionary['t'] in BLOCK and without_write:  # parse it only if it is inside table
                self.write_special_block(dictionary)
            elif dictionary['t'] in CODE and not without_write:  # parse it only if it is outside table
                self.write_code(dictionary)
            elif dictionary['t'] == 'Para' and without_write:
                self.add_content('\n')
            elif 'c' in dictionary and without_write:
                if type(dictionary['c']) == str:
                    self.add_content(dictionary['c'])
                if type(dictionary['c']) == list:
                    self.list_parse(dictionary['c'], without_write)
            elif without_write:  # blocks without content
                if dictionary['t'] == 'Space':
                    self.add_content(' ')
                elif dictionary['t'] == 'SoftBreak':
                    self.add_content('\n')
                elif dictionary['t'] == 'LineBreak':
                    self.add_content('\n\n')
        except KeyError:
            print('Untypical block. Some information might be lost.')

    def list_parse(self, content_list, without_write=False):
        """Parse list.

        Args:
            content_list - list with different parts of content from input-document.
            without_write - indicate calling write_text() functions. By default calls it.
        """
        for item in content_list:
            if type(item) == dict:
                self.dict_parse(item, without_write)
            elif type(item) == list:
                self.list_parse(item, without_write)
            else:
                print('Untypical block. Some information might be lost.')

    def main(self, document):
        """Main function.
        Gets JSON object from Pandoc, parses it and extracts tables.

        Args:
            doc - json object as python dictionary or list.
                  In case of dictionary it has representation like:
                  { 'pandoc-version': ...
                    'meta': ...
                    'blocks': .......}
                  in blocks we have all file-content, we will parse doc['blocks'].
                  In case of list it has representation like:
                  [[info_list], [content_list]], so we will parse doc[1].
        """

        if type(document) == dict:
            self.list_parse(document['blocks'])
        elif type(document) == list:
            self.list_parse(document[1])
        else:
            print('Incompatible Pandoc version')

    def parse(self, source):
        command = 'pandoc ' + source + ' -t json'
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = proc.communicate()
        if res[1]:
            print(str(res[1]))  # sending stderr output to user
        else:
            document = json.loads(res[0])
            self.main(document)
            return self.tables
