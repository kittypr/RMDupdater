import json
import subprocess

from copy import copy

TABLE = ('Table', )
CODE = ('Code', 'CodeBlock')
BLOCK = ('Div', 'Header', 'Span')


class TableExtractor:

    def __init__(self):
        self.tables = dict()
        self.context = ''
        self.ancestor = ''
        self.content = ''

    def get_content(self):
        content = copy(self.content)
        self.content = ''
        return content

    def add_content(self, addition):
        self.content = self.content + addition

    def save_ancestor(self, ancestor):
        self.context = copy(self.ancestor)
        self.ancestor = ancestor

    def write_code(self, code):
        """Saves code block that creates other elements in case ones were changed.
        Since, element with title 'Code' or 'CodeBlock' has special structure of 'c'(Content) field, that looks like:
        [[0], 'code']
        where:
            [0] - list of attributes: identifier, classes, key-value pairs.
            'code' - string with code.
        we should parse it especially.
        Args:
            code - element with title 'Code' or 'CodeBlock'.
        """
        self.save_ancestor(code['c'][1])

    def write_special_block(self, block):
        con = 1
        if block['t'] == 'Header':
            con = 2
        self.list_parse(block['c'][con], cell_content=True)

    def write_table(self, tab):
        """Extracts table and saves them with code block they were made from.
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
                self.list_parse(col, cell_content=True)
                cell_content = self.get_content()
                row.append(cell_content)
            table.append(row)
        t_content = tab['c'][4]
        for line in t_content:
            row = list()
            for col in line:
                self.list_parse(col, cell_content=True)
                cell_content = self.get_content()
                row.append(cell_content)
            table.append(row)
        self.tables[((self.context, self.ancestor), len(self.tables))] = table

    def dict_parse(self, dictionary, cell_content=False):
        """Parse dictionaries.
        Dictionary represents some json-object. The kind of json object depends on its 't' (title) field.
        We will parse it differently depending on different titles.

        Args:
            dictionary - object with 't' and sometimes 'c' fields.
            cell_content - indicates either we inside or outside of table cell
        """
        try:
            if dictionary['t'] in TABLE:  # blocks that may have content
                self.write_table(dictionary)
            elif dictionary['t'] in BLOCK and cell_content:  # parse it only if it is inside table
                self.write_special_block(dictionary)
            elif dictionary['t'] in CODE and not cell_content:  # parse it only if it is outside table
                self.write_code(dictionary)
            elif dictionary['t'] == 'Para' and cell_content:
                self.add_content('\n')
            elif 'c' in dictionary and cell_content:
                if type(dictionary['c']) == str:
                    self.add_content(dictionary['c'])
                if type(dictionary['c']) == list:
                    self.list_parse(dictionary['c'], cell_content)
            elif cell_content:  # blocks without content
                if dictionary['t'] == 'Space':
                    self.add_content(' ')
                elif dictionary['t'] == 'SoftBreak':
                    self.add_content(' ')
                elif dictionary['t'] == 'LineBreak':
                    self.add_content('\n')
        except KeyError:
            print('Untypical block. Some information might be lost.')

    def list_parse(self, content_list, cell_content=False):
        """Parse list.

        Args:
            content_list - list with different parts of content from input-document.
            cell_content - indicates either we inside or outside of table cell
        """
        for item in content_list:
            if type(item) == dict:
                self.dict_parse(item, cell_content)
            elif type(item) == list:
                self.list_parse(item, cell_content)
            else:
                print('Untypical block. Some information might be lost.')

    def document_parse(self, document):
        """Main function.
        Gets JSON object from Pandoc, parses it and extracts tables.

        Args:
            document - json object as python dictionary or list.
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
            print('Incompatible Pandoc version. Process failed.')

    def parse(self, source):
        command = 'pandoc ' + source + ' -t json'
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = proc.communicate()
        if res[1]:
            print('PROCESS FAILED. SEE BELOW:')
            print(str(res[1]))
            return None  # sending stderr output to user
        else:
            document = json.loads(res[0])
            self.document_parse(document)
            return self.tables
