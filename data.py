import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from collections import Counter
import demoji

colorlist = [
    "#D8DDEC",
    "#D4EBD4",
    "#EFEED8",
    "#F9DFE1",
    "#F6D0E8",
    "#DFF2FD",
    "#E2FCE6",
    "#FCFADE",
    "#FFEEE2",
    "#FFDBDB",
    "#F692BC",
    "#F4ADC6",
    "#FDFD95",
    "#AAC5E2",
    "#6891C3",
    "#77DD77",
]


colorlist = [
    "#D8DDEC",
    "#D4EBD4",
    "#EFEED8",
    "#F9DFE1",
    "#F6D0E8",
    "#DFF2FD",
    "#E2FCE6",
    "#FCFADE",
    "#FFEEE2",
    "#FFDBDB",
    "#F692BC",
    "#F4ADC6",
    "#FDFD95",
    "#AAC5E2",
    "#6891C3",
    "#77DD77",
]


def clean_data(df):
    def getdate(x):
        res = re.search("\d\d/\d\d/\d\d", x)
        if res != None:
            return res.group()
        else:
            return ""

    df["Date"] = list(map(lambda x: getdate(x), df.iloc[:, 0]))

    ## Merge multiline chat data

    for i in range(0, len(df)):
        if df["Date"][i] == "":
            c = i - 1
            for j in range(i, len(df)):
                if df["Date"][j] == "":
                    df.iloc[c, 0] = " ".join([df.iloc[c, 0], df.iloc[j, 0]])

                else:
                    i = j - 1
                    break
        else:
            df.iloc[i, 0] = df.iloc[i, 0]

    ## Remove rows where date is empty
    df.drop(np.where(df.iloc[:, 1] == "")[0], inplace=True)

    def gettime(x):
        res = re.search(".\d:\d\d\s[a|p]m", x)
        if res != None:
            return res.group()
        else:
            return ""

    df["time"] = df[0].apply(gettime)
    df["Hour"] = df["time"].apply(lambda x: x.split(":")[0])
    df["Minute"] = df["time"].apply(lambda x: x.split(":")[1].split(" ")[0])
    df["AmPm"] = df["time"].apply(lambda x: x.split(":")[1].split(" ")[1])

    ## Extract Day Month and Year from Date
    df["Day"] = list(map(lambda d: d.split("/")[0], df.Date))
    df["Months"] = list(map(lambda d: d.split("/")[1], df.Date))
    df["Year"] = list(map(lambda d: d.split("/")[2], df.Date))

    ##Remove date from original text data using substitute function of regular expression
    df.iloc[:, 0] = list(map(lambda x: re.sub("../../..", "", x)[2:], df.iloc[:, 0]))
    ## Remove Timestamps from chat
    df.iloc[:, 0] = list(
        map(lambda x: re.sub(".*\d:\d\d\s[a|p]m", "", x)[2:], df.iloc[:, 0])
    )

    def getsender(x):
        res = re.search(re.compile(".*?: "), x)
        if res != None:
            return res.group()[1:-2]
        else:
            return ""

    df["sender"] = list(map(getsender, df.iloc[:, 0]))
    df = df[df["sender"].notna()]

    ## extract final message from chat data
    def getmessage(x):
        res = re.search(": .*", x)
        if res != None:
            return res.group()[2:]
        else:
            return None

    df["Message"] = list(map(getmessage, df.iloc[:, 0]))

    df = df.dropna()
    df.drop([0], axis=1, inplace=True)
    ## Reindex the dataframe
    df = df.reset_index(drop=True)
    return df


def sender_msg_count(df):
    op = (
        df["sender"]
        .value_counts()
        .rename_axis("sender")
        .to_frame("message counts")
        .sort_values("message counts")
    )
    return op, round(op["message counts"].mean(), 0)


def activity_wrt_time(df):

    ## creating groups of data by time meridian
    timemeridian = df.groupby(by="AmPm")

    amhours = timemeridian.get_group("am")
    pmhours = timemeridian.get_group("pm")

    ## getting hourly activity counts
    amhourcounts = amhours.Hour.value_counts().sort_index()
    pmhourcounts = pmhours.Hour.value_counts().sort_index()

    fig = plt.figure(figsize=[20, 10])

    gs = GridSpec(2, 3)  # 2 rows and 3 columns
    ax1 = fig.add_subplot(gs[0, 1])  # first row, second col
    ax2 = fig.add_subplot(gs[1, 1])  # second row, second col
    ax3 = fig.add_subplot(gs[:, 2])  # all row, third col

    # Bar plot for messages shared in AM time meridian
    ax1.bar(amhourcounts.index, amhourcounts.values, color="black")
    ax1.set(xlabel="hour AM")
    # Bar plot for messages shared in PM time meridian
    ax2.bar(pmhourcounts.index, pmhourcounts.values, color="black")
    ax2.set(xlabel="hour PM")

    # Bar plot showing AM vs PM
    ax3.bar(["AM", "PM"], [len(amhours), len(pmhours)], color="green")
    ax3.annotate(
        text=str(round(100 * len(amhours) / (len(amhours) + len(pmhours)))) + "%",
        xy=[0, len(amhours) / 2],
        color="white",
        size=14,
        horizontalalignment="center",
    )
    ax3.annotate(
        text=str(round(100 * len(pmhours) / (len(amhours) + len(pmhours)))) + "%",
        xy=[1, len(pmhours) / 2],
        color="white",
        size=14,
        horizontalalignment="center",
    )
    ax3.set(title="percentage of message AM vs PM")
    return fig


def top_active_days_avgmsg(df):
    top_10_active_days = (
        df["Date"].value_counts().rename_axis("unique_values").to_frame("counts")
    )
    top_10_active_days.sort_values("counts", inplace=True)
    avg_msg_per_day = top_10_active_days.mean()
    avg_msg_per_day_num = round(avg_msg_per_day[0], 0)
    top_10_active_daysnew = top_10_active_days[-10:]

    # fig, ax = plt.subplots()
    # ax.bar(x=top_10_active_daysnew.index, height=top_10_active_daysnew.values)
    return top_10_active_daysnew, avg_msg_per_day_num


def total_media_shared(df):
    df["Media"] = (
        df["Message"]
        .astype(str)
        .apply(lambda x: 1 if ("media omitted") in x.lower() else 0)
    )
    media = (
        df[df["Media"] == 1]["sender"]
        .value_counts()
        .rename_axis("Members")
        .to_frame("counts")
    )
    return media["counts"].sum(), media


def word_cloud(df):
    words = " ".join(df["Message"].apply(str))

    def punctuation_stop(text):
        filtered = []
        stop_words = set(STOPWORDS)
        word_tokens = text.split()
        for w in word_tokens:
            if w not in stop_words and w.isalpha():
                filtered.append(w.lower())
        return filtered

    words_filtered = punctuation_stop(words)

    text = " ".join([ele for ele in words_filtered])

    wc = WordCloud(
        background_color="white",
        random_state=1,
        stopwords=STOPWORDS,
        max_words=50,
        width=1000,
        height=1500,
    )
    wordcloud = wc.generate(text)
    fig1 = plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")

    cmnwrd = Counter(words.split()).most_common(20)

    wrd = []
    cnt = []
    for i in cmnwrd:
        wrd.append(i[0])
        cnt.append(i[1])

    gs = pd.DataFrame(list(zip(cnt, wrd)), columns=["count", "words"]).set_index(
        "words"
    )

    fig2 = plt.figure()
    plt.plot(gs["count"], linestyle="-")
    plt.xticks(rotation=60)
    plt.ylabel("total message count")
    return fig1, fig2


def emojie_count(df):
    li = []
    for i in df["Message"].apply(str):

        for j in demoji.findall(i).keys():
            li.append(j)

    d = Counter(li)
    op = pd.DataFrame.from_dict(d, columns=["Count"], orient="index")
    op = op.sort_values("Count", ascending=False)
    return op[:10]


def word_letter_counter(df):
    df2 = df[df["Message"] == "<Media omitted>"]
    df1 = df.copy()
    df1 = df1.drop(df2.index)

    df1["Letter_Count"] = df1["Message"].apply(str).apply(lambda s: len(s))
    df1["Word_Count"] = df1["Message"].apply(str).apply(lambda s: len(s.split(" ")))

    average_letter_per_message = round(df1["Letter_Count"].mean(), 0)
    average_word_per_message = round(df1["Word_Count"].mean(), 0)
    total_letters = df1["Letter_Count"].sum()
    total_word = df1["Word_Count"].sum()
    total_deleted_messages = df[df["Message"].str.contains("message was deleted")][
        "Day"
    ].count()

    return (
        average_letter_per_message,
        average_word_per_message,
        total_letters,
        total_word,
        total_deleted_messages,
    )


def time_series(df):
    format = "%d/%m/%y %H:%M %p"
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["time"], format=format)
    df_date = df.set_index(pd.DatetimeIndex(df["Datetime"]))
    df_o = df_date.groupby("Date").count()["Day"]
    fig1 = plt.figure(figsize=[15, 7])
    plt.plot(df_o, linestyle="-")
    plt.xticks(rotation=60)
    plt.ylabel("total message count")

    ini_time = df_date.index[0]
    fin_time = df_date.index[-1]
    tot_time = fin_time - ini_time

    chat_started_datetime = "Chat started on - {} {}".format(
        ini_time, df["AmPm"].iat[0]
    )
    last_chat_datetime = "Last chat on - {} {}".format(fin_time, df["AmPm"].iat[-1])
    sttoend = "Out of {} days {} days members pinged.".format(
        tot_time.days, df["Date"].nunique()
    )
    return fig1, chat_started_datetime, last_chat_datetime, sttoend
