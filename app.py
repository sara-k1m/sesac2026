import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.set_page_config(
    page_title="HR 퇴직현황",
    layout="wide"
)

st.title("HR 퇴직현황 대시보드")

# 1. 데이터 불러오기
df = pd.read_csv("HR Data.csv")

# 연령대 생성
df["연령대"] = pd.cut(
    df["나이"],
    bins=[0, 29, 39, 49, 59, 100],
    labels=["20대 이하", "30대", "40대", "50대", "60대 이상"]
)

# 근속구간 생성
# 2년 이하, 3~5년, 6~10년, 11년 이상
df['근속구간'] = pd.cut(
    df['근속연수'],
    bins=[-1, 2, 5, 10, 100],
    labels = ['2년 이하', '3~5년', '6~10년', '11년 이상']
)

# 월급여구간 생성
# 하위 25%, 25~50%, 50~75%, 상위 25%
df['월급여구간'] = pd.qcut(
    df['월급여'],
    q=4,
    labels = ['하위 25%', '25~50%', '50~75%', '상위 25%']
)

# 2. 사이드바
st.sidebar.header("조회 조건")

department = st.sidebar.selectbox(
    "부서를 선택하세요",
    ["전체"] + sorted(df["부서"].unique())
)

overtime = st.sidebar.selectbox(
    "야근 여부를 선택하세요",
    ["전체"] + sorted(df["야근정도"].unique())
)

# 3. 데이터 필터링
result = df.copy()

if department != "전체":
    result = result[result["부서"] == department]

if overtime != "전체":
    result = result[result["야근정도"] == overtime]

# 4. KPI
employee_count = len(result)
retired_count = (result["퇴직여부"] == "Yes").sum()
retired_rate = retired_count / employee_count * 100

col1, col2, col3 = st.columns(3)

col1.metric("총 직원 수", f"{employee_count}명")
col2.metric("퇴직자 수", f"{retired_count}명")
col3.metric("퇴직률", f"{retired_rate:.1f}%")

st.divider()

# 5. 그래프 데이터
# 부서별 퇴직률
tenure_result = (
    result.groupby("근속구간", observed=False)["퇴직여부"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="퇴직률")
)

# 연령대별 퇴직률
age_result = (
    result.groupby("연령대", observed=False)["퇴직여부"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="퇴직률")
)

# 월급여구간별 퇴직률
income_result = (
    result.groupby("월급여구간", observed=False)["퇴직여부"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="퇴직률")
)

# 6. 그래프
graph_col1, graph_col2, graph_col3 = st.columns(3)

# 근속구간별
with graph_col1:

    st.subheader("근속구간별 퇴직률")

    fig1, ax1 = plt.subplots(figsize=(6,4))

    sns.barplot(
        data=tenure_result,
        x="근속구간",
        y="퇴직률",
        ax=ax1
    )

    ax1.axhline(
        retired_rate,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"평균 {retired_rate:.1f}%"
    )

    for container in ax1.containers:
        ax1.bar_label(container, fmt="%.1f")

    ax1.set_xlabel("퇴직률(%)")
    ax1.set_ylabel("")
    ax1.legend()

    st.pyplot(fig1)

# 연령대별
with graph_col2:

    st.subheader("연령대별 퇴직률")

    fig2, ax2 = plt.subplots(figsize=(6,4))

    sns.barplot(
        data=age_result,
        x="연령대",
        y="퇴직률",
        ax=ax2
    )

    ax2.axhline(
        retired_rate,
        color="red",
        linestyle="--",
        label=f"평균 {retired_rate:.1f}%"
    )

    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.1f")

    ax2.set_ylabel("퇴직률(%)")
    ax2.legend()

    st.pyplot(fig2)

# 월급여구간별
with graph_col3:

    st.subheader("월급여구간별 퇴직률")

    fig3, ax3 = plt.subplots(figsize=(6,4))

    sns.barplot(
        data=income_result,
        x="월급여구간",
        y="퇴직률",
        ax=ax3
    )

    ax3.axhline(
        retired_rate,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"평균 {retired_rate:.1f}%"
    )

    for container in ax3.containers:
        ax3.bar_label(container, fmt="%.1f")

    ax3.set_xlabel("월급여 구간")
    ax3.set_ylabel("퇴직률(%)")
    ax3.legend()

    st.pyplot(fig3)

# 7. 데이터 보기
st.subheader("필터링된 데이터")
st.dataframe(result)
