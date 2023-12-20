import pandas as pd
import os

if __name__ == '__main__':
    # csvs = [
    #     pd.read_csv(os.path.join("src", f), header=0, quotechar='"')
    #     for f in os.listdir('src/') if ".csv" in f
    # ]
    #
    # data = pd.concat(csvs)
    # data.sort_values("index", inplace=True)
    # data.set_index("index", inplace=True)
    # data.to_csv("src/csv/unbalanced_train_segments.csv")

    data = pd.read_csv(os.path.join("src/csv", "unbalanced_train_segments.csv"),
                       header=0, quotechar='"')
    data1 = data.iloc[:len(data)//2]
    data2 = data.iloc[len(data)//2:]
    data1.to_csv("src/csv/unbalanced_train_segments_1.csv", index=False)
    data2.to_csv("src/csv/unbalanced_train_segments_2.csv", index=False)