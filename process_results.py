import pandas as pd

def plot_time(data: pd.DataFrame):
    grouped = data.groupby(["Binary", "Profile", "Dataset"])["UserTime(s)"].agg(["min", "max", "mean", "std"])
    print(grouped)

def plot_memory(data: pd.DataFrame):
    grouped = data.groupby(["Binary", "Profile", "Dataset"])["MaxRSS(KB)"].agg(["min", "max", "mean", "std"])
    print(grouped)

def check_correctness(data: pd.DataFrame):
    grouped = data.groupby(["Binary", "Profile", "Dataset"])["TP", "FP", "FN", "Patterns"].agg(["min", "max"])
    print(grouped)

def main():
    data = pd.read_csv("evaluation_results.csv")
    
    plot_time(data)

    plot_memory(data)

    check_correctness(data)

if __name__ == "__main__":
    main()
