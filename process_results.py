import pandas as pd

def process_time(data: pd.DataFrame):
    grouped = pd.DataFrame(data.groupby(["Binary", "Profile", "Dataset"])["UserTime(s)"].agg(["min", "max", "mean", "std"]))
    grouped.to_csv("time.csv")

def process_memory(data: pd.DataFrame):
    grouped = pd.DataFrame(data.groupby(["Binary", "Profile", "Dataset"])["PeakMemory(KB)"].agg(["min", "max", "mean", "std"]))
    grouped.to_csv("memory.csv")

def check_correctness(data: pd.DataFrame):
    pd.DataFrame(data.groupby(["Binary", "Profile", "Dataset"])[["Good", "Bad", "Missed", "Patterns"]].agg(["min", "max"])).to_csv("correctness.csv", header=["Good_min", "Good_max", "Bad_min", "Bad_max", "Missed_min", "Missed_max", "Patterns_min", "Patterns_max"])

def main():
    data = pd.read_csv("evaluation_results.csv")
    
    process_time(data)

    process_memory(data)

    check_correctness(data)

if __name__ == "__main__":
    main()
