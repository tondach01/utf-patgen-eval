import pandas as pd
import typing

def process_column(data: pd.DataFrame,
                   column_name: str,
                   export_name: str,
                   filter_dataset: typing.Union[str, None] = None,
                   filter_profile: typing.Union[str, None] = None):
    grouped = data.groupby(["Binary", "Profile", "Dataset"], as_index=False)[column_name].agg(["mean", "std"])

    if filter_dataset is not None:
        grouped = grouped[grouped["Dataset"] == filter_dataset]
    if filter_profile is not None:
        grouped = grouped[grouped["Profile"] == filter_profile]
    
    # exclude experiments that failed with output limit exception and round std
    grouped = grouped[
        (grouped["Binary"] != "patgen") |
        (grouped["Profile"] == "cshyphen.in") |
        (grouped["Profile"] == "wortliste.in") |
        (grouped["Dataset"] != "de_wortliste")
    ].round({"std": 2, "mean": 2}) # pyright: ignore[reportArgumentType]
    
    grouped_patgen = grouped[grouped["Binary"] == "patgen"].drop(columns=["Binary"])
    grouped_utfpatgen = grouped[grouped["Binary"] == "utfpatgen"].drop(columns=["Binary"])

    ratios = pd.merge(grouped_patgen, grouped_utfpatgen, on=["Profile", "Dataset"], suffixes=("_p", "_u"))
    ratios["\\patgen"] = ratios.apply(lambda row: f"{row['mean_p']} ({row['std_p']})", axis=1)
    ratios["\\utfpatgen"] = ratios.apply(lambda row: f"{row['mean_u']} ({row['std_u']})", axis=1)
    ratios["Ratio"] = ratios["mean_u"] / ratios["mean_p"]
    
    ratios = ratios.drop(columns=["mean_p", "std_p", "mean_u", "std_u"]).round({"Ratio": 3})
    sort_columns = ["Dataset", "Profile", "Ratio"]
    if filter_dataset is not None:
        ratios = ratios.drop(columns=["Dataset"])
        sort_columns.remove("Dataset")
    if filter_profile is not None:
        ratios = ratios.drop(columns=["Profile"])
        sort_columns.remove("Profile")
    ratios = ratios.sort_values(by=sort_columns)
    ratios = ratios[["Dataset", "Profile", "\\patgen", "\\utfpatgen", "Ratio"]]

    ratios.to_csv(f"{export_name}.csv", index=False)

def process_time(data: pd.DataFrame):
    process_column(data, "UserTime(s)", "time")

def process_memory(data: pd.DataFrame):
    process_column(data, "PeakMemory(KB)", "memory")

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
