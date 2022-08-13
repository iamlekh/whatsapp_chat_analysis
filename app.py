import streamlit as st
import pandas as pd
import .data
import numpy as np
import matplotlib.pyplot as plt

st.title("WHATSAPP CHAT ANALYSIS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.header("Step 1")
    st.caption("Click on Options")
    st.image(
        "https://raw.githubusercontent.com/iamlekh/whatsapp-chat-analyser/main/app/static/img/step1.png",
    )

with col2:
    st.header("Step 1")
    st.caption("Click on More")
    st.image(
        "https://raw.githubusercontent.com/iamlekh/whatsapp-chat-analyser/main/app/static/img/step2.png"
    )

with col3:
    st.header("Step 1")
    st.caption("Click on Export Chat")
    st.image(
        "https://raw.githubusercontent.com/iamlekh/whatsapp-chat-analyser/main/app/static/img/step3.png"
    )

with col4:
    st.header("Step 1")
    st.caption("Click on Without Media")
    st.image(
        "https://raw.githubusercontent.com/iamlekh/whatsapp-chat-analyser/main/app/static/img/step4.png"
    )

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    try:
        dataframe = pd.read_csv(
            uploaded_file,
            sep="delimiter",
            skip_blank_lines=True,
            header=None,
            engine="python",
        )

        st.title("clean data")
        df1 = data.clean_data(dataframe)
        st.dataframe(df1)

        sender_msg = data.sender_msg_count(df1)[0]

        total_menber = (
            f"You have total -- {len(sender_msg.index)} -- members in the group."
        )
        st.subheader(total_menber)

        st.pyplot(data.activity_wrt_time(df1))

        avg_msg = data.top_active_days_avgmsg(df1)[1]
        st.subheader(f"Average messages per day {avg_msg}")

        st.bar_chart(data.top_active_days_avgmsg(df1)[0])

        iterator_marks = iter(data.sender_msg_count(df1)[0].index)
        l = len(data.sender_msg_count(df1)[0].index)
        for _ in range(l):

            if (l % 2) == 0:
                try:
                    col1, col2 = st.columns(2)
                    a = next(iterator_marks)
                    b = next(iterator_marks)
                    col1.metric(
                        a,
                        data.sender_msg_count(df1)[0]["message counts"][a],
                        data.sender_msg_count(df1)[0]["message counts"][a]
                        - data.sender_msg_count(df1)[1],
                    )
                    col2.metric(
                        b,
                        data.sender_msg_count(df1)[0]["message counts"][b],
                        data.sender_msg_count(df1)[0]["message counts"][b]
                        - data.sender_msg_count(df1)[1],
                    )
                except StopIteration:
                    break
            else:
                try:
                    col1, col2 = st.columns(2)
                    a, b = next(iterator_marks), next(iterator_marks)
                    col1.metric(
                        a,
                        data.sender_msg_count(df1)[0]["message counts"][a],
                        data.sender_msg_count(df1)[0]["message counts"][a]
                        - data.sender_msg_count(df1)[1],
                    )
                    col2.metric(
                        b,
                        data.sender_msg_count(df1)[0]["message counts"][a],
                        data.sender_msg_count(df1)[0]["message counts"][b]
                        - data.sender_msg_count(df1)[1],
                    )
                except StopIteration:
                    break
                else:
                    c = next(iterator_marks)
                    st.metric(
                        c,
                        data.sender_msg_count(df1)[0]["message counts"][c],
                        data.sender_msg_count(df1)[0]["message counts"][c]
                        - data.sender_msg_count(df1)[1],
                    )

        st.subheader("user vs message")

        st.bar_chart(sender_msg)

        st.subheader(f"Total media file shared -- {data.total_media_shared(df1)[0]}")

        st.table(data.total_media_shared(df1)[1])

        st.pyplot(data.word_cloud(df1)[0])

        st.table(data.emojie_count(df1))

        st.markdown("""---""")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write(f"Total words in the chat --  {data.word_letter_counter(df1)[3]}")
        with col2:
            st.write(
                f"Total letters in the chat --  {data.word_letter_counter(df1)[2]}"
            )

        with col3:
            st.write(f"Average words per message -- {data.word_letter_counter(df1)[1]}")
        with col4:
            st.write(
                f"average letters per message   -- {data.word_letter_counter(df1)[0]}"
            )

        st.markdown("""---""")

        st.pyplot(data.time_series(df1)[0])
        st.markdown("""---""")
        st.subheader(data.time_series(df1)[1])
        st.subheader(data.time_series(df1)[2])
        st.subheader(data.time_series(df1)[3])

        st.markdown("""---""")
        st.subheader(f"total deleted messages {data.word_letter_counter(df1)[4]}")
        st.markdown("""---""")

        st.pyplot(data.word_cloud(df1)[1])
    except Exception as e:
        st.subheader("please upload the doc in proper format")
