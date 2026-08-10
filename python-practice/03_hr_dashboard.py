import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import koreanize_matplotlib

# import 추가
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)
MODEL = "gpt-4o-mini"

# 페이지 설정
st.set_page_config(page_title="HR 퇴직 분석", page_icon="📊", layout="wide")
st.title("📊 HR 퇴직 현황 대시보드")
st.write("부서와 근속연수를 선택하여 퇴직 현황을 확인합니다.")


# 데이터 불러오기
@st.cache_data
def load_data():
    data = pd.read_csv("HR Data.csv")

    # 퇴직 여부를 0과 1로 변환
    data["퇴직"] = data["퇴직여부"].map({"No": 0, "Yes": 1})

    # 연령대 생성
    data["연령대"] = pd.cut(
        data["나이"],
        bins=[0, 29, 39, 49, 59, 100],
        labels=["20대 이하", "30대", "40대", "50대", "60대 이상"]
    )

    return data

df = load_data()


# 전체 퇴직률 계산
overall_rate = df["퇴직"].mean() * 100


# 사이드바 조회 조건
st.sidebar.title("조회 조건")

dept = st.sidebar.selectbox(
    "부서를 선택하세요",
    ["전체"] + sorted(df["부서"].unique())
)

min_tenure, max_tenure = st.sidebar.slider(
    "근속연수를 선택하세요",
    min_value=int(df["근속연수"].min()),
    max_value=int(df["근속연수"].max()),
    value=(int(df["근속연수"].min()), int(df["근속연수"].max()))
)


# 데이터 필터링
hr = df.copy()

if dept != "전체":
    hr = hr[hr["부서"] == dept]

hr = hr[hr["근속연수"].between(min_tenure, max_tenure)]


# 선택한 조건에 데이터가 없는 경우
if hr.empty:
    st.warning("선택한 조건에 해당하는 직원이 없습니다.")
    st.stop()


# 선택 집단의 KPI 계산
total_employees = len(hr)
total_attritions = int(hr["퇴직"].sum())
filtered_rate = hr["퇴직"].mean() * 100
rate_difference = filtered_rate - overall_rate


# KPI 출력
col1, col2, col3 = st.columns(3)

col1.metric("선택 직원 수", f"{total_employees:,}명")
col2.metric("퇴직자 수", f"{total_attritions:,}명")
col3.metric(
    "선택 집단 퇴직률",
    f"{filtered_rate:.1f}%",
    delta=f"전체 대비 {rate_difference:+.1f}%p",
    delta_color="inverse"
)

st.caption(f"비교 기준인 전체 직원의 퇴직률은 {overall_rate:.1f}%입니다.")


# 퇴직 통계표 생성 함수
def attrition_summary(data, group_column):
    result = data.groupby(group_column, observed=True).agg(
        직원수=("퇴직", "size"),
        퇴직자수=("퇴직", "sum"),
        퇴직률=("퇴직", "mean")
    ).reset_index()

    result["퇴직률"] = (result["퇴직률"] * 100).round(1)
    return result.sort_values("퇴직률", ascending=False)


# 통계표 생성
age_result = attrition_summary(hr, "연령대")
overtime_result = attrition_summary(hr, "야근정도")


# 그래프 출력
graph_col1, graph_col2 = st.columns(2)

# 첫 번째 그래프
graph_col1.subheader("연령대별 퇴직률")

fig1, ax1 = plt.subplots(figsize=(6, 4))

sns.barplot(data=age_result, x="연령대", y="퇴직률", ax=ax1)

ax1.axhline(
    overall_rate,
    color="red",
    linestyle="--",
    label=f"전체 {overall_rate:.1f}%"
)

ax1.set_xlabel("연령대")
ax1.set_ylabel("퇴직률(%)")
ax1.tick_params(axis="x", rotation=15)
ax1.legend()

graph_col1.pyplot(fig1)
plt.close(fig1)


# 두 번째 그래프
graph_col2.subheader("야근 정도별 퇴직률")

fig2, ax2 = plt.subplots(figsize=(6, 4))

sns.barplot(data=overtime_result, x="야근정도", y="퇴직률", ax=ax2)

ax2.axhline(
    overall_rate,
    color="red",
    linestyle="--",
    label=f"전체 {overall_rate:.1f}%"
)

ax2.set_xlabel("야근 정도")
ax2.set_ylabel("퇴직률(%)")
ax2.legend()

graph_col2.pyplot(fig2)
plt.close(fig2)


# ====================================AI 인사이트 생성================================================

dept_text = '전체'if dept == '전체' else f"{dept} 부서"
selectede_members = f"{dept} 부서에서 근속연수가 {min_tenure}년 이상 {max_tenure}년 이하인 직원 {total_employees}명"

# 통계표
age_text = age_result.to_csv(index=False)
overtime_text = overtime_result.to_csv(index=False)

prompt = f"""
당신은 15년 경력의 HR 데이터 분석가입니다.
아래 분석 결과를 바탕으로 인사담당자가 바로 실무에 참고할 수 있는 인사이트를 작성하세요.

[분석 대상]
조회 대상: {selectede_members}
퇴직자 수: {total_attritions}명
전체 퇴직률: {overall_rate:.1f}%
조회대상 퇴직률: {filtered_rate:.1f}%
전체대비 차이: {rate_difference:+.1f}%p

[연령대별 퇴직률]
{age_text}

[야근정도별 퇴직률]
{overtime_text}

다음 JSON 형식으로만 답변하세요. 다른 텍스트나 코드블록 표시(```) 없이 순수 JSON만 출력합니다.

{{
  "risk_level": "낮음 | 보통 | 높음 중 택1 (전체 대비 퇴직률 차이 기준으로 판단)",
  "target_summary": "조회 대상을 한 문장으로 요약 (숫자 포함)",
  "key_findings": [
    "핵심 발견 1 (반드시 수치 근거 포함, 30자 내외)",
    "핵심 발견 2 (반드시 수치 근거 포함, 30자 내외)"
  ],
  "recommendations": [
    "권장 조치 1 (구체적 실행 방안, 30자 내외)",
    "권장 조치 2 (구체적 실행 방안, 30자 내외)"
  ]
}}

작성 기준:
- key_findings와 recommendations는 반드시 위에 제공된 통계 수치를 근거로 작성 (막연한 일반론 금지)
- recommendations는 실제로 HR 부서가 이번 주에 실행 가능한 수준의 구체성을 가질 것
- risk_level은 rate_difference의 절대값이 3%p 미만이면 "낮음", 3~7%p면 "보통", 7%p 이상이면 "높음"
"""

import json

if st.button("🤖 AI 인사이트 생성", use_container_width=True):
    with st.spinner("AI가 데이터를 분석하고 있습니다..."):
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=MODEL,
            input=prompt,
        )

    try:
        insight = json.loads(response.output_text)
    except json.JSONDecodeError:
        st.error("AI 응답을 해석하지 못했습니다. 다시 시도해주세요.")
        st.stop()

    # 위험도에 따른 색상/아이콘 매핑
    risk_map = {
        "낮음": ("🟢", "success"),
        "보통": ("🟡", "warning"),
        "높음": ("🔴", "error"),
    }
    icon, color = risk_map.get(insight["risk_level"], ("⚪", "info"))

    st.divider()

    # 상단: 분석대상 + 위험도 배지
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(f"**🎯 분석 대상**")
        st.write(insight["target_summary"])
    with header_col2:
        getattr(st, color)(f"{icon} 위험도: {insight['risk_level']}")

    # 핵심요약 / 권장조치를 나란히 카드로 배치
    finding_col, action_col = st.columns(2)

    with finding_col:
        with st.container(border=True):
            st.markdown("**💡 핵심 요약**")
            for item in insight["key_findings"]:
                st.markdown(f"- {item}")

    with action_col:
        with st.container(border=True):
            st.markdown("**✅ 권장 조치**")
            for item in insight["recommendations"]:
                st.markdown(f"- {item}")

if st.button("AI 인사이트 생성"):
    # AI 모델에 질문을 보내고 답변을 받는 부분
    client = OpenAI(api_key = api_key)
    response = client.responses.create(
        model=MODEL,
        input =prompt,
    )

    st.write(response.output_text)