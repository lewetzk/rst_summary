from pathlib import Path


def main():
    orderfile = Path("order.txt")
    summ25 = Path("summarized_25k.txt")
    summ50 = Path("summarized_50k.txt")

    with orderfile.open(encoding="utf-8") as order, summ25.open(encoding="utf-8") as s25, summ50.open(encoding="utf-8") as s50:
        for order_file, su2, su5 in zip(order, s25, s50):
            path = Path(f"../summaries/neural/")
            filepath25 = Path(f"{path}/25k")
            filepath50 = Path(f"{path}/50k")

            path.mkdir(parents=True, exist_ok=True)
            filepath25.mkdir(parents=True, exist_ok=True)
            filepath50.mkdir(parents=True, exist_ok=True)

            Path(f"{filepath25}/{order_file.strip()}").write_text(su2)
            Path(f"{filepath50}/{order_file.strip()}").write_text(su5)


if __name__ == "__main__":
    main()
