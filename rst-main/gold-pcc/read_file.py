# usage: python read_file.py < file_to_read

import re
import sys
from io import TextIOWrapper

#sys.stdin.reconfigure(encoding='utf-8')
#sys.stdout.reconfigure(encoding='utf-8')

pattern = re.compile(r"\[([^\]]+)]([0-9])")

for line in TextIOWrapper(sys.stdin.buffer, encoding='utf-8'):
    for result in re.findall(pattern, line):
        print(result[-1], result[0])  # sentence n, sentence
