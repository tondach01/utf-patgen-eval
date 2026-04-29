import re
import argparse
import os

HYPHENATION_MARKER = "-"

class HyphenationDataset:
    def __init__(self, name: str, filepath: str = ""):
        self.name: str = name
        self.mapping: "dict[str,str]" = dict()
        if filepath:
            self.fill(filepath)

    def fill(self, filepath: str):
        with open(filepath) as dictionary:
            for entry in dictionary:
                entry = re.sub(r"[0-9]", "", entry.strip()).lower()
                word = re.sub(HYPHENATION_MARKER, "", entry)
                self.mapping[word] = entry

    def compare_to(self, other: "HyphenationDataset", full_report: bool = False, report_dir: str = ".") -> "tuple[int,int]":
        in_both: int = 0
        conflicts: int = 0
        report_file = None
        if full_report:
            report_file = open(f"{report_dir}/{self.name}_{other.name}_report.txt", "w")
        for common_word in set(other.mapping.keys()).intersection(set(self.mapping.keys())):
            in_both += 1
            if other.mapping[common_word] != self.mapping[common_word]:
                if report_file is not None:
                    print(f"{self.mapping[common_word]} {other.mapping[common_word]}", file=report_file)
                conflicts += 1
        if report_file is not None:
            report_file.close()
            if conflicts == 0:
                os.remove(f"{report_dir}/{self.name}_{other.name}_report.txt")
        return in_both, conflicts
    
    def resolve_conflict(self, entry_1: str, entry_2: str) -> str:
        hyphen_positions: list[int] = []
        idx_1: int = 0
        idx_2: int = 0
        for i in range(len(re.sub(HYPHENATION_MARKER, "", entry_1))):
            if entry_1[i + idx_1] == HYPHENATION_MARKER and entry_2[i + idx_2] == HYPHENATION_MARKER:
                hyphen_positions.append(i)
            if entry_1[i + idx_1] == HYPHENATION_MARKER:
                idx_1 += 1
            if entry_2[i + idx_2] == HYPHENATION_MARKER:
                idx_2 += 1
        new_entry: str = ""
        for i, c in enumerate(re.sub(HYPHENATION_MARKER, "", entry_1)):
            if i in hyphen_positions:
                new_entry += HYPHENATION_MARKER
            new_entry += c
        return new_entry
    
    def distinct_characters(self) -> int:
        characters: set[str] = set()
        for word in self.mapping.keys():
            characters.update(set(word))
        return len(characters)
    
    def average_line(self) -> float:
        line_count = 0
        character_sum = 0
        for word in self.mapping.values():
            line_count += 1
            character_sum += len(word)
        return character_sum / line_count
    
    def average_hyphens(self) -> float:
        line_count = 0
        hyphen_count = 0
        for word in self.mapping.values():
            line_count += 1
            hyphen_count += word.count(HYPHENATION_MARKER)
        return hyphen_count / line_count
    
    def join(self, other: "HyphenationDataset", new_name: str = "") -> "HyphenationDataset":
        joined: HyphenationDataset = HyphenationDataset(new_name if new_name else f"{self.name}+{other.name}")
        joined.mapping = self.mapping.copy()
        for word, entry in other.mapping.items():
            if word in joined.mapping and entry != joined.mapping[word]:
                joined.mapping[word] = joined.resolve_conflict(entry, joined.mapping[word])
            elif word not in joined.mapping:
                joined.mapping[word] = entry
        return joined
    
    def export(self, name: str = "", dir: str = ".") -> str:
        outfile = f"{name}.wlh" if name else f"{self.name}.wlh"
        with open(dir + "/" + outfile, "w") as out:
            for entry in self.mapping.values():
                print(entry, file=out)
        return outfile
    
    def __str__(self):
        return f""",{self.name}
Number of lines,{len(self.mapping)}
Average line length,{round(self.average_line(),2)}
Average hyphen count per line,{round(self.average_hyphens(),2)}
Number of distinct characters,{self.distinct_characters()}"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--configfile", type=str, required=True, help="Language configuration file")
    parser.add_argument("-o", "--outdir", type=str, required=False, default=".", help="Output directory")
    args = parser.parse_args()

    datasets: "list[HyphenationDataset]" = []

    combined_dataset = HyphenationDataset(f"{args.configfile.split('/')[-1].rsplit('.', maxsplit=1)[0]}")
    
    with open(args.configfile) as langs:
        for lang in langs:
            parsed = lang.split()
            if len(parsed) < 2:
                continue
            new_dataset = HyphenationDataset(parsed[0], parsed[1])
            datasets.append(new_dataset)
            combined_dataset = combined_dataset.join(new_dataset, combined_dataset.name)
    
    combined_dataset.export(dir = args.outdir)

    with open("conflicts.csv", "w") as conf:
        print("Dataset 1,Dataset 2,Intersection,Conflicts", file=conf)
        for i in range(len(datasets)):
            for j in range(i+1,len(datasets)):
                intersection, conflicts = datasets[i].compare_to(datasets[j], full_report=True, report_dir=args.outdir)
                print(f"{datasets[i].name},{datasets[j].name},{intersection},{conflicts}", file=conf)
    
    with open("combined_dataset.csv", "w") as comb:
        print(str(combined_dataset),file=comb)

if __name__ == "__main__":
    main()
