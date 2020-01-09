class yufile(object):
    def __init__(self, path):
        self.path = path

    def openfile(self):
        try:
            with open(self.path, 'r') as f:
                string = f.read()
            return string
        except Exception as e:
            return ''

    def writefile(self, string):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(string)