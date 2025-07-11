import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Analyze time intervals between operations in a session log"
    )
    parser.add_argument(
        "dat_file",
        help="Path to the .dat file containing session logs",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Delimiter used in the .dat file (default: comma)",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Specify when the input file does not contain a header row",
    )
    return parser.parse_args()


def load_data(path, delimiter=",", no_header=False):
    """Load the log data as a ``pandas.DataFrame``.

    Parameters
    ----------
    path : str
        Path to the log file.
    delimiter : str, optional
        Delimiter used in the log file.
    no_header : bool, optional
        If ``True``, the file is parsed without a header row.

    Returns
    -------
    pandas.DataFrame
        Loaded log data with ``timestamp`` parsed as ``datetime``.
    """

    column_names = ["session_id", "timestamp", "item_id", "category"]

    if no_header:
        df = pd.read_csv(
            path,
            delimiter=delimiter,
            names=column_names,
            header=None,
            dtype=str,
        )
    else:
        df = pd.read_csv(path, delimiter=delimiter, dtype=str)

        # If the required columns are missing, try interpreting the file
        # as header-less (common with yoochoose datasets).
        if "timestamp" not in df.columns or "session_id" not in df.columns:
            df = pd.read_csv(
                path,
                delimiter=delimiter,
                names=column_names,
                header=None,
                dtype=str,
            )

    if "timestamp" not in df.columns or "session_id" not in df.columns:
        raise ValueError(
            "Input data must contain 'session_id' and 'timestamp' columns"
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"])
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
    df = load_data(args.dat_file, delimiter=args.delimiter, no_header=args.no_header)
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
