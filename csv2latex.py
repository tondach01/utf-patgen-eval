import argparse
import re

def put_line(line: str, outfile):
    values = line.strip().split(",")
    print("\t" + " & ".join([escape(v) for v in values]) + " \\\\", file=outfile)

def enclose(s: str) -> str:
    return "{" + s + "}"

def escape(s: str) -> str:
    escaped = s
    escaped = re.sub("_", "\\_", escaped)
    escaped = re.sub("&", "\\&", escaped)
    escaped = re.sub("%", "\\%", escaped)
    return escaped

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--csvfile", required=True, type=str, help="CSV file to convert")
    parser.add_argument("-o", "--outputfile", required=False, type=str, default="table.txt", help="Output file name")
    parser.add_argument("-l", "--label", required=False, type=str, default="", help="Table label")
    parser.add_argument("-d", "--description", required=False, type=str, default="A table", help="Long table description")
    parser.add_argument("-s", "--shortdescription", required=False, type=str, default="", help="Short table description")
    args = parser.parse_args()

    csv = open(args.csvfile, "r")
    out = open(args.outputfile, "w")

    print("\\begin{table}".format(table=enclose("table")), file=out)
    print("\t\\caption{short}{long}".format(short=(f"[{escape(args.shortdescription)}]" if args.shortdescription else ""), long=enclose(escape(args.description))), file=out)
    if args.label:
        print("\t\\label{label}".format(label=enclose(escape(args.label))), file=out)
    print("\t\\centering", file=out)

    line = csv.readline().strip()
    print("\t\\begin{tabular}{signature}".format(tabular=enclose("tabular"), signature=enclose(" " + ' '.join(['c' for _ in line.split(',')]) + " ")), file=out)
    print("\t\\toprule", file=out)
    put_line(line, out)
    print("\t\\midrule", file=out)

    line = csv.readline().strip()
    while line:
        put_line(line, out)
        line = csv.readline().strip()
    print("\t\\bottomrule", file=out)

    print("\t\\end{tabular}".format(tabular=enclose("tabular")), file=out)
    print("\\end{table}".format(table=enclose("table")), file=out)

if __name__ == "__main__":
    main()
