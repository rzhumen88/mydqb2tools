from PIL import Image

def main():
    font = Image.open('00000784.a8.dds')
    w, h = font.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = font.getpixel((x,y))
            if a > 0x80:
                r, g, b = (0xB0,0xB0,0xB0)
            font.putpixel((x,y), (r,g,b,a))
    font.show()

if __name__ == '__main__':
    main()
