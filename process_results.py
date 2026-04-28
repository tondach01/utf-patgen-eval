import pandas as pd

def process_time(data: pd.DataFrame):
    grouped = pd.DataFrame(data.groupby(["Binary", "Profile", "Dataset"], as_index=False)["UserTime(s)"].agg(["min", "max", "mean", "std"]))

    # exclude experiments that failed with output limit exception
    grouped = grouped[
        (grouped["Binary"] != "patgen") |
        (grouped["Profile"] == "cshyphen.in") |
        (grouped["Profile"] == "wortliste.in") |
        (grouped["Dataset"] != "de_wortliste")
    ].round({"std": 2})

    grouped.to_csv("time.csv", index=False)

def process_memory(data: pd.DataFrame):
    grouped = pd.DataFrame(data.groupby(["Binary", "Profile", "Dataset"], as_index=False)["PeakMemory(KB)"].agg(["min", "max", "mean", "std"]))
    
    # exclude experiments that failed with output limit exception
    grouped = grouped[
        (grouped["Binary"] != "patgen") |
        (grouped["Profile"] == "cshyphen.in") |
        (grouped["Profile"] == "wortliste.in") |
        (grouped["Dataset"] != "de_wortliste")
    ].round({"std": 2})
    
    grouped.to_csv("memory.csv", index=False)

def check_correctness(data: pd.DataFrame):
    grouped = data.groupby(["Profile", "Dataset"], as_index=False)[["Good", "Bad", "Missed", "Patterns"]].agg(
        Good_min=("Good", "min"),
        Good_max=("Good", "max"),
        Bad_min=("Bad", "min"),
        Bad_max=("Bad", "max"),
        Missed_min=("Missed", "min"),
        Missed_max=("Missed", "max"),
        Patterns_min=("Patterns", "min"),
        Patterns_max=("Patterns", "max")
    )
    grouped = grouped[
        (grouped["Good_min"] != grouped["Good_max"]) |
        (grouped["Bad_min"] != grouped["Bad_max"]) |
        (grouped["Missed_min"] != grouped["Missed_max"]) |
        (grouped["Patterns_min"] != grouped["Patterns_max"])
    ]
    grouped.to_csv("correctness.csv", index=False)

def check_stability(data: pd.DataFrame):
    grouped = data.groupby(["Binary", "Profile", "Dataset"], as_index=False)[["Good", "Bad", "Missed", "Patterns"]].agg(
        Good_min=("Good", "min"),
        Good_max=("Good", "max"),
        Bad_min=("Bad", "min"),
        Bad_max=("Bad", "max"),
        Missed_min=("Missed", "min"),
        Missed_max=("Missed", "max"),
        Patterns_min=("Patterns", "min"),
        Patterns_max=("Patterns", "max")
    )
    grouped = grouped[
        (grouped["Good_min"] != grouped["Good_max"]) |
        (grouped["Bad_min"] != grouped["Bad_max"]) |
        (grouped["Missed_min"] != grouped["Missed_max"]) |
        (grouped["Patterns_min"] != grouped["Patterns_max"])
    ]
    grouped.to_csv("stability.csv", index=False)

def main():
    data = pd.read_csv("evaluation_results.csv")
    
    process_time(data)

    process_memory(data)

    check_correctness(data)

    check_stability(data)

if __name__ == "__main__":
    main()
