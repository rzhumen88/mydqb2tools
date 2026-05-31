import os
import struct
import zlib

class DQB2BIN:
    
    def __init__(self):
        self.clear()
        self.canBeExported = False
        
    def clear(self):
        self.bin = None
        self.idx = None
        self.fileList = {}
        self.canBeExported = False
        
    def read(self, idx, bin_):
        self.canBeExported = True
        with open(idx, 'rb') as self.idx:
            self.idx = self.idx.read()
            self.bin = bin_
            self.j = 0
            for i in range(0, len(self.idx), 32):
                self.offset, _, self.compressedSize, _, self.sectors, _, self.isCompressed, _ = struct.unpack('IIIIIIII', self.idx[i:i+32])
                if self.isCompressed == 1:
                    self.isCompressed = True
                else:
                    self.isCompressed = False
                self.fileList[self.j] = (self.offset, self.compressedSize, self.sectors, self.isCompressed)
                self.j += 1

    def extract(self):
        if self.canBeExported:
            if os.path.isfile('extracted/'+'list.txt'): os.remove('extracted/'+'list.txt')
            if not os.path.isdir('extracted'):
                os.mkdir('extracted')
            for self.i in range(len(self.fileList)):
                self.offset, self.compressedSize, self.sectors, self.isCompressed = self.fileList[self.i]
                with open(self.bin, 'rb') as self.f:
                    with open('extracted/'+'list.txt', 'a') as self.txt:
                        self.extName = 'extracted/'+str(self.i).zfill(8)
                        with open(self.extName, 'wb') as self.f2:
                            self.txt.write(f'{self.extName}, {self.isCompressed}\n')
                            if self.compressedSize + self.sectors == 0:
                                pass
                            else:
                                self.f.seek(self.offset)
                                if not self.isCompressed:
                                    self.f2.write(self.f.read(self.compressedSize))
                                else:
                                    self.fileHeader = self.f.read(12)
                                    self.header, self.parts, self.uncompressedSize = struct.unpack('III', self.fileHeader)
                                    self.fileHeader = self.f.read(self.parts*4)
                                    self.partsSizes = struct.unpack('I'*self.parts, self.fileHeader)
                                    self.k = self.offset + 12 + (self.parts*4)
                                    while not self.k % 0x80 == 0:
                                        self.k += 1
                                    self.f.seek(self.k)
                                    self.k = 0
                                    self.parts = []
                                    self.chunk = self.f.read(self.sectors)
                                    for self.j in self.partsSizes:
                                        self.parts.append(self.chunk[self.k:self.k+self.j])
                                        self.k += self.j
                                        while not self.k % 0x80 == 0:
                                            self.k += 1
                                    for self.part in self.parts:
                                        self.partUncomSize = struct.unpack('I', self.part[:4])[0]
                                        try:
                                            self.uncompressedPart = zlib.decompress(self.part[4:])
                                        except zlib.error:
                                            self.uncompressedPart = self.part
                                        self.f2.write(self.uncompressedPart)
                                print(f'Extracted: {self.extName} Size: {round(self.uncompressedSize/1024, 2)}kb Compressed: {self.isCompressed}')

    def buildRaw(self, folder: str):
        """doesn't work properly"""
        self.folder = folder.rstrip('/').rstrip(r'\\')
        self.clear()
        self.offset = 0
        self.filesize = 0
        self.files = os.listdir(self.folder)
        self.totalInFolder = len(self.files)
        with open(f'{self.folder}.idx', 'wb') as self.idx:
            with open(f'{self.folder}.bin', 'wb') as self.bin:
                for self.fileid in range(0, self.totalInFolder):
                    self.filename = f'{self.folder}/{str(self.fileid).zfill(8)}'
                    if os.path.isfile(self.filename):
                        with open(self.filename, 'rb') as self.f:
                            self.f = self.f.read()
                            self.filesize = len(self.f)
                            self.fileinfo = struct.pack('I'*8, self.offset, 0, self.filesize, 0, self.filesize, 0, 0, 0)
                            self.idx.write(self.fileinfo)
                            self.bin.write(self.f)
                            self.offset += self.filesize
                            self.i = 0
                            while self.offset % 0x100 != 0:
                                self.offset += 1
                                self.i += 1
                            self.bin.write(b'\x00'*self.i)
                            print(f'File {self.fileid} imported!')
                    else:
                        self.fileinfo = struct.pack('I'*8, self.offset, 0, 0, 0, 0, 0, 0, 0)
                        self.idx.write(self.fileinfo)
                        print(f'File {self.fileid} skipped!')

if __name__ == '__main__':
    a = DQB2BIN()
    a.read('LINKDATA.IDX', 'LINKDATA.BIN')
    a.extract()
    #a.buildRaw('extracted/')
    input('Done!')
