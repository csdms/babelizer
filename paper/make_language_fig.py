import matplotlib.pyplot as plt
import pandas as pd


def main():
    if 0:
        data = pd.read_html("https://csdms.colorado.edu/wiki/CSDMS_models_by_numbers")[
            2
        ]

        languages = pd.DataFrame(
            {"Count": data["Count"].values}, index=data["Program language"]
        )
        languages.to_csv("languages.csv")
    else:
        languages = pd.read_csv("languages.csv", index_col=0, header=0)

    other = languages[languages["Count"] < 10]
    languages.loc["Other", "Count"] += other["Count"].sum()
    languages = languages[languages["Count"] >= 10]

    languages.sort_index(inplace=True)

    # explode = [0.1, 0.1, 0.1, 0.1, 0.0, 0.0, 0.1]
    explode = [0.1] * len(languages)

    plt.pie(
        languages["Count"],
        autopct="%1.1f%%",
        labels=languages.index,
        explode=explode,
        shadow=True,
    )
    plt.show()


if __name__ == "__main__":
    main()
