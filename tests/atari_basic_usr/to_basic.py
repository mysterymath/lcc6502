import argparse

parser = argparse.ArgumentParser()
parser.add_argument("binary", help="The binary file to load into 0x600")
args = parser.parse_args()


with open(args.binary, 'rb') as f:
    data = f.read()

    print("10 FOR I = 1536 TO", 1536+len(data)-1)
    print("20 READ D")
    print("30 POKE I,D")
    print("40 NEXT I")
    line = 50
    for i in range(0, len(data), 8):
        print(line, "DATA ", end='')
        print(*data[i:i + 8], sep=',')
        line += 10
