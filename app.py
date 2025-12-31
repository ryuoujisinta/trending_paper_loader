# 標準ライブラリ
import datetime
import os

# サードパーティライブラリ
import streamlit as st

# ローカルモジュール
from config import config
from data_processing import (
    deduplicate_papers,
    filter_papers,
    sort_papers_by_date,
    sort_papers_by_upvotes,
)
from utils import load_data, save_data, fetch_daily_papers_from_hf

# Page config
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT
)


# Custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"{file_name} not found.")


local_css("css/style.css")

# --- Main App ---

st.sidebar.title("Trending Paper Dashboard")

# Date Selection (GMT/UTC)
today = datetime.datetime.now(datetime.timezone.utc).date()

# Mode Selection
date_mode = st.sidebar.radio("日付選択モード", ["単一日付", "期間指定"], horizontal=True)

if 'single_date' not in st.session_state:
    st.session_state.single_date = today

if date_mode == "単一日付":
    col_prev, col_date, col_next = st.sidebar.columns([1, 2.5, 1])

    def prev_day():
        st.session_state.single_date -= datetime.timedelta(days=1)

    def next_day():
        if st.session_state.single_date < today:
            st.session_state.single_date += datetime.timedelta(days=1)

    with col_prev:
        st.button("◀", key="prev_date", on_click=prev_day, use_container_width=True)

    with col_next:
        st.button("▶", key="next_date", on_click=next_day, use_container_width=True)

    with col_date:
        st.date_input(
            "日付選択",
            max_value=today,
            format="YYYY/MM/DD",
            key="single_date",
            label_visibility="collapsed"
        )

    start_date = end_date = st.session_state.single_date

else:  # 期間指定
    date_selection = st.sidebar.date_input(
        "期間選択",
        value=(today, today),
        max_value=today,
        format="YYYY/MM/DD"
    )

    # Resolve date range
    if isinstance(date_selection, tuple):
        if len(date_selection) == 2:
            start_date, end_date = date_selection
        elif len(date_selection) == 1:
            start_date = end_date = date_selection[0]
        else:
            start_date = end_date = today
    else:
        start_date = end_date = date_selection

search_query = st.sidebar.text_input("検索キーワード (保存データ内)", "")

# Sorting Option
sort_option = st.sidebar.radio("並び替え", ["日付順 (新着順)", "Upvote数順"], horizontal=True)


# Helper to generate date list
def daterange(start, end):
    for n in range(int((end - start).days) + 1):
        yield start + datetime.timedelta(n)


# 1. Load Data across range
papers = []
missing_dates = []
loaded_dates = []

for single_date in daterange(start_date, end_date):
    date_str = single_date.strftime("%Y-%m-%d")
    daily_data = load_data(date_str)
    if daily_data:
        papers.extend(daily_data)
        loaded_dates.append(single_date)
    else:
        missing_dates.append(single_date)

# Manual Upvote Update Button in Sidebar
if loaded_dates:
    if st.sidebar.button("最新のUpvote数を取得"):
        from utils import get_upvotes_map
        progress_bar = st.sidebar.progress(0, text="Upvote取得中...")
        total = len(loaded_dates)

        for i, d in enumerate(loaded_dates):
            d_str = d.strftime("%Y-%m-%d")
            try:
                upvotes_map = get_upvotes_map(d)
                if upvotes_map:
                    # Update existing JSON data
                    daily_data = load_data(d_str)
                    if daily_data:
                        updated = False
                        for p in daily_data:
                            pid = p.get('id')
                            if pid in upvotes_map:
                                p['upvotes'] = upvotes_map[pid]
                                updated = True
                        if updated:
                            save_data(d_str, daily_data)
            except Exception as e:
                st.error(f"{d_str} のUpvote更新中にエラーが発生しました: {e}")
                st.stop()  # Stop execution as requested
            progress_bar.progress((i + 1) / total)

        st.sidebar.success("Upvote数を更新しました")
        st.rerun()

# Deduplication (Keep LATEST occurrence and highest upvotes)
papers = deduplicate_papers(papers)

# Header
if start_date == end_date:
    header_text = f"{start_date} のトレンド論文"
else:
    header_text = f"{start_date} 〜 {end_date} のトレンド論文"
st.header(header_text)

# 2. Fetch Logic
if missing_dates:
    st.info(f"未取得の日付があります: {', '.join([d.strftime('%Y-%m-%d') for d in missing_dates])}")
    if st.button("不足分のデータを取得・保存する"):
        progress_text = "データを一括取得中..."
        my_bar = st.progress(0, text=progress_text)

        total_steps = len(missing_dates)
        current_step = 0

        newly_fetched_count = 0

        for d in missing_dates:
            d_str = d.strftime("%Y-%m-%d")

            # Inner progress callback for single day?
            # We can simplify: just update main bar per day for simplicity.
            # Or make it granular. Let's do main bar per day for simplicity.
            my_bar.progress(current_step / total_steps, text=f"{d_str} のデータを取得中...")

            # Sub-progress for the day could be nice but streamlit bars don't nest easily without complexity.
            # We will pass None to utils and just wait.
            # Or we can use a placeholder for detail status.

            with st.spinner(f"{d_str} のデータをスクレイピング中..."):
                # We won't use the granular callback inside fetch to avoid fighting with the outer bar
                # separate status text is enough.
                try:
                    daily_papers = fetch_daily_papers_from_hf(d)
                    if daily_papers:
                        save_data(d_str, daily_papers)
                        newly_fetched_count += len(daily_papers)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    st.stop()  # Stop execution as requested

            current_step += 1
            my_bar.progress(current_step / total_steps, text=f"{d_str} 完了")

        my_bar.progress(1.0, text="全完了")
        st.success(f"合計 {newly_fetched_count} 件のデータを取得しました。")
        st.rerun()


# Refetch Button (Update existing)
if loaded_dates:
    st.caption(f"読み込み済み: {len(papers)} 件 ({len(loaded_dates)} 日分)")
    if st.button("表示中の期間をすべて再取得 (更新)"):
        # Similar loop but for all dates in range
        progress_text = "データを更新中..."
        my_bar = st.progress(0, text=progress_text)
        total_steps = (end_date - start_date).days + 1
        current_step = 0

        for d in daterange(start_date, end_date):
            d_str = d.strftime("%Y-%m-%d")
            my_bar.progress(current_step / total_steps, text=f"{d_str} を更新中...")
            with st.spinner(f"{d_str} を更新中..."):
                try:
                    daily_papers = fetch_daily_papers_from_hf(d)
                    if daily_papers:
                        save_data(d_str, daily_papers)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    st.stop()  # Stop execution as requested
            current_step += 1

        my_bar.progress(1.0, text="更新完了")
        st.success("データを更新しました。")
        st.rerun()

# 3. Filter & Display
if papers:
    # Sorting logic
    if sort_option == "Upvote数順":
        papers_sorted = sort_papers_by_upvotes(papers, reverse=True)
    else:
        # Default: Newest First
        papers_sorted = sort_papers_by_date(papers, reverse=True)

    # Filtering
    filtered_papers = filter_papers(papers_sorted, search_query)

    if filtered_papers:
        st.write(f"表示: {len(filtered_papers)} / {len(papers)} 件")

        for i, paper in enumerate(filtered_papers):
            # Display-time thumbnail override
            if paper.get('id'):
                paper['thumbnail'] = config.CDN_THUMBNAIL_URL_TEMPLATE.format(paper_id=paper['id'])

            with st.container(border=True):
                c1, c2 = st.columns([1, 2])

                with c1:
                    st.markdown(f"### {paper['title']}")

                    # Display upvotes and date
                    upvotes = paper.get('upvotes', '0')
                    st.markdown(f"❤️ **{upvotes}** &nbsp;&nbsp; | &nbsp;&nbsp; 📅 {paper.get('date')}")

                    if paper.get('thumbnail'):
                        st.image(paper['thumbnail'], width="stretch")

                    st.caption(f"ID: {paper.get('id', '')}")
                    st.markdown(f"[元記事を読む]({paper['link']})", unsafe_allow_html=True)

                with c2:
                    st.markdown("#### Abstract")
                    st.write(paper.get('summary', ''))

    else:
        if search_query:
            st.warning("検索条件に一致する論文はありません。")
else:
    # If no missing dates but no papers (e.g. all empty files?) or start state
    if not missing_dates:
        st.warning("表示できるデータがありません。")
