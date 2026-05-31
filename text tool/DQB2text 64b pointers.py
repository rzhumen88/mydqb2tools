import os
import struct
import rusconverter
from translate import Translator

class DQB2Text:
    def __init__(self):
        self.clean()

    def __len__(self):
        return len(self.ids)

    def clean(self):
        self.ids = []
        self.pointers = []
        self.unk = []
        self.strings = []
        self.autotranslated = []

    def getstrings(self):
        return self.strings

    def getpointers(self):
        return self.pointers

    def getids(self):
        return self.ids

    def getautotranslated(self):
        return self.autotranslated

    def setautotranslated(self, autotranslated):
        self.autotranslated = autotranslated

    def setids(self, ids: list):
        self.ids = ids

    def setstrings(self, strings: list):
        self.strings = strings
        
    def setpointers(self, pointers: list):
        self.pointers = pointers

    def readfile(self, path: str):
        self.clean()
        with open(path, 'rb') as self.f:
            self.header = self.f.read(0x40)
            self.total = struct.unpack('I', self.header[:4])[0]
            self.f.seek(0x40)
            self.ids = struct.unpack('I'*self.total, self.f.read(self.total * 4))
            for _ in range(self.total):
                self.pointers.append(struct.unpack('I', self.f.read(4))[0])
                self.unk.append(struct.unpack('I', self.f.read(4))[0])
            self.f.seek(0x40 + (self.total * 4))
            self.f = self.f.read()
            for self.p in range(self.total):
                self.line = b''
                self.p = self.pointers[self.p]
                self.i = 0
                while not self.f[self.p + self.i] == 0:
                    self.line += struct.pack('B', self.f[self.p + self.i])
                    self.i += 1
                self.f = self.f[8:]
                try:
                    self.strings.append(self.line.decode('utf8'))
                except UnicodeDecodeError:
                    self.strings.append('CANT DECODE')

    def writefile(self, path: str):
        if len(self) == 0:
            raise RuntimeError(f"{type(self).__name__} has no strings")
        with open(path, 'wb') as self.f:
            self.buffer = b''
            self.textbuffer = b''
            self.buffer += struct.pack('I', len(self))
            self.buffer += b'\x00' * 60
            print(self.unk)
            for self.i in range(len(self.ids)):
                self.buffer += struct.pack('I', self.ids[self.i])
            self.i = len(self) * 4
            self.pointers = [self.i, ]
            for self.s in self.strings:
                self.s = self.s.encode('utf8') + b'\x00'
                self.textbuffer += self.s
                self.i -= 4
                self.i += len(self.s)
                self.pointers.append(self.i)
            self.pointers = self.pointers[:-1]
            if len(self.ids) != len(self.pointers):
                raise RuntimeError(f"Unmatch: ids={len(self.ids)} pointers={len(self.pointers)}")
            for self.i in range(len(self.pointers)):
                self.buffer += struct.pack('I', self.pointers[self.i])
                self.buffer += struct.pack('I', self.unk[self.i])
            self.f.write(self.buffer)
            self.f.write(self.textbuffer)

    def savetext(self, path: str):
        with open(path, 'w', encoding='utf8') as self.txt:
            for self.i in range(len(self.ids)):
                self.txt.write(f'{self.ids[self.i]}: {self.strings[self.i]}\n')
                if self.autotranslated != []:
                    self.txt.write(f'{self.ids[self.i]}: {self.autotranslated[self.i]}\n')
                else:
                    self.txt.write(f'{self.ids[self.i]}: {self.strings[self.i]}\n')  #if you don't need double writing - comment this line
                self.txt.write(f'{self.ids[self.i]}: {self.unk[self.i]}\n')

    def readfromtxt(self, path: str):
        self.clean()
        with open(path, 'r', encoding='utf8') as self.txt:
            self.txt = self.txt.readlines()
            for self.i in range(0, len(self.txt), 3):
                self.id, self.string = self.txt[self.i+1].split(': ', 1)
                _, self.speakerid = self.txt[self.i+2].split(': ', 1)
                self.ids.append(int(self.id))
                self.unk.append(int(self.speakerid.rstrip()))
                self.strings.append(self.string.replace('\n', ''))

    def autotranslate(self, lang: str):
        self.autotranslated = []
        self.tra = Translator(lang)
        for self.s in self.strings:
            self.autotranslated.append(self.tra.translate(self.s))

def main():
    while True:
        print('---DQB2text 64-bit pointers---')
        method = input('Enter [i] if you want to convert txt to game file.\nEnter [e] if you want to convert game file to txt.')
        path = input('Enter path to file: ')
        if not os.path.isfile(path):
            raise ValueError(f'File {path} does not exist!')
        autotranslate = None
        text = DQB2Text()
        match method:
            case 'i':
                text.readfromtxt(path)
                strings = text.getstrings()
                for i in range(len(text)):
                    strings[i] = rusconverter.convert(strings[i])
                text.setstrings(strings)
                text.writefile(path+'.unpack')
            case 'e':
                auto = input('Do you want to autotranslate the file [y/n]: ')
                if auto == 'y':
                    autotranslate = input('Your language [ru, en]: ')
                text.readfile(path)
                if autotranslate:
                    print('autotranslating...')
                    text.autotranslate(autotranslate)
                text.savetext(path+'.txt')
            case _:
                pass
        input('done')

main()
