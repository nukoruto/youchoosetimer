import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze time intervals between operations in a session log")
    parser.add_argument("dat_file", help="Path to the .dat file containing session logs")
    parser.add_argument("--delimiter", default=",", help="Delimiter used in the .dat file (default: comma)")
    return parser.parse_args()


def load_data(path, delimiter=","):
    df = pd.read_csv(path, delimiter=delimiter)
    # Expect columns: session_id, operation, timestamp
    if 'timestamp' not in df.columns:
        raise ValueError("Input data must contain a 'timestamp' column")
    if 'session_id' not in df.columns:
        raise ValueError("Input data must contain a 'session_id' column")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def compute_diffs(df):
    df_sorted = df.sort_values(['session_id', 'timestamp'])
    df_sorted['time_diff'] = df_sorted.groupby('session_id')['timestamp'].diff().dt.total_seconds()
    return df_sorted.dropna(subset=['time_diff'])


def describe_diffs(diffs):
    mean = diffs.mean()
    std = diffs.std(ddof=1)
    n = diffs.count()
    conf_int = (mean - 1.96 * std / np.sqrt(n), mean + 1.96 * std / np.sqrt(n))
    percentiles = diffs.quantile([0.025, 0.975]).to_list()
    return mean, std, n, conf_int, percentiles


def plot_histogram(diffs):
    plt.hist(diffs, bins=30, edgecolor='black')
    plt.xlabel('Time difference (s)')
    plt.ylabel('Count')
    plt.title('Distribution of operation intervals per session')
    plt.show()


def main():
    args = parse_arguments()
    df = load_data(args.dat_file, delimiter=args.delimiter)
    diffs_df = compute_diffs(df)
    diffs = diffs_df['time_diff']

    mean, std, n, conf_int, percentiles = describe_diffs(diffs)
    print(f"Number of intervals: {n}")
    print(f"Mean: {mean:.2f}s, Std: {std:.2f}s")
    print(f"95% Confidence interval of the mean: [{conf_int[0]:.2f}, {conf_int[1]:.2f}] seconds")
    print(f"2.5th-97.5th percentile range: [{percentiles[0]:.2f}, {percentiles[1]:.2f}] seconds")

    plot_histogram(diffs)


if __name__ == "__main__":
    main()
