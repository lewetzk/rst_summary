import argparse
from pathlib import Path
import re

from baseline_random_summary import read_text_body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    inputpath = Path(args.path)
    outputpath = Path("oneliner")
    outputpath.mkdir(parents=True, exist_ok=True)
    oneliner = Path(f"{outputpath}/oneliner.txt")
    orderfle = Path(f"{outputpath}/order.txt")

    pattern = re.compile(r"\s+")
    
    with oneliner.open("w", encoding="utf-8") as oneliner_file:
        with orderfle.open("w", encoding="utf-8") as order_file:
            for filename in inputpath.iterdir():
                _, sents = read_text_body(filename)
                text = " ".join(sents)
                order_file.write(f"{filename.name}\n")
                single_line = re.sub(pattern, " ", text)
                
                oneliner_file.write(f"{single_line}\n")




if __name__ == "__main__":
    main()