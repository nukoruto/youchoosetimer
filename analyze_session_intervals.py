import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Analyze time intervals between events in a CSV log"
    )
    parser.add_argument(
        "csv_file",
        help="Path to the CSV file containing session logs",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Delimiter used in the CSV file (default: comma)",
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

    column_names = [
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid",
    ]

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
        # as header-less.
        if "timestamp" not in df.columns or "visitorid" not in df.columns:
            df = pd.read_csv(
                path,
                delimiter=delimiter,
                names=column_names,
                header=None,
                dtype=str,
            )

    if "timestamp" not in df.columns or "visitorid" not in df.columns:
        raise ValueError(
            "Input data must contain 'visitorid' and 'timestamp' columns"
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # map events to READ/UPDATE/COMMIT labels
    event_map = {
        "view": "READ",
        "addtocart": "UPDATE",
        "transaction": "COMMIT",
    }
    if "event" in df.columns:
        df["event"] = df["event"].map(event_map).fillna(df["event"])

    return df


def compute_diffs(df):
    """Calculate time differences between successive events per visitor.

    The returned frame contains ``time_diff`` and ``transition`` columns.
    """

    df_sorted = df.sort_values(["visitorid", "timestamp"])
    df_sorted["prev_event"] = df_sorted.groupby("visitorid")["event"].shift()
    df_sorted["time_diff"] = (
        df_sorted.groupby("visitorid")["timestamp"].diff().dt.total_seconds()
    )
    df_sorted["transition"] = (
        df_sorted["prev_event"].fillna("START")
        + "->"
        + df_sorted["event"].fillna("UNKNOWN")
    )
    return df_sorted.dropna(subset=["time_diff"])  # drop first event per visitor


def describe_diffs(diffs):
    mean = diffs.mean()
    std = diffs.std(ddof=1)
    n = diffs.count()
    conf_int = (mean - 1.96 * std / np.sqrt(n), mean + 1.96 * std / np.sqrt(n))
    percentiles = diffs.quantile([0.025, 0.975]).to_list()
    return mean, std, n, conf_int, percentiles


def plot_histogram(diffs, title=None):
    plt.hist(diffs, bins=30, edgecolor="black")
    plt.xlabel("Time difference (s)")
    plt.ylabel("Count")
    if title:
        plt.title(title)
    else:
        plt.title("Distribution of operation intervals")
    plt.show()


def main():
    args = parse_arguments()
    df = load_data(args.csv_file, delimiter=args.delimiter, no_header=args.no_header)
    diffs_df = compute_diffs(df)

    for transition, group in diffs_df.groupby("transition"):
        diffs = group["time_diff"]
        mean, std, n, conf_int, percentiles = describe_diffs(diffs)
        print(f"\nTransition: {transition}")
        print(f"  Number of intervals: {n}")
        print(f"  Mean: {mean:.2f}s, Std: {std:.2f}s")
        print(
            f"  95% CI: [{conf_int[0]:.2f}, {conf_int[1]:.2f}] seconds"
        )
        print(
            f"  2.5th-97.5th percentile range: [{percentiles[0]:.2f}, {percentiles[1]:.2f}] seconds"
        )

        plot_histogram(diffs, title=f"{transition} interval distribution")


if __name__ == "__main__":
    main()
