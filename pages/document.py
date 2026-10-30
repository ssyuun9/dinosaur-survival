
import streamlit as st
import urllib.request
import urllib.parse
import json

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="공룡 도감",
    page_icon="🦖",
    layout="wide"
)

# ==========================================
# 2. 공룡 데이터
# ==========================================

DINOSAURS = {
    "트라이아스기": [
        "헤레라사우루스", "스타우리코사우루스", "에오랍토르",
        "코엘로피시스", "릴리엔스테르누스", "프로콤프소그나투스",
        "에우디모르포돈", "플라테오사우루스", "리오자사우루스",
        "무사우루스", "안키사우루스", "세라토사우루스",
        "타니스트로페우스", "노토사우루스", "쇼니사우루스",
        "믹소사우루스", "심보스폰딜루스", "프테로닥틸루스",
        "람포린쿠스", "프레온닥틸루스", "스카포그나투스",
        "포스토수쿠스", "리스트로사우루스"
    ],

    "쥐라기": [
        "알로사우루스", "케라토사우루스", "딜로포사우루스",
        "메갈로사우루스", "토르보사우루스", "마르쇼사우루스",
        "콤프소그나투스", "오르니톨레스테스", "신랍토르",
        "양추아노사우루스", "모노로포사우루스", "크리올로포사우루스",
        "아파토사우루스", "브라키오사우루스", "디플로도쿠스",
        "카마라사우루스", "바로사우루스", "슈노사우루스",
        "마멘키사우루스", "슈퍼사우루스", "세이스모사우루스",
        "케티오사우루스", "투리아사우루스", "스테고사우루스",
        "켄트로사우루스", "화양고사우루스", "미라가이아",
        "드라코펠타", "가고사우루스", "에우로펠타",
        "캄토사우루스", "드리오사우루스", "오스니엘리아",
        "헤테로돈토사우루스", "리코리누스", "아브릭토사우루스",
        "오트니엘로사우루스", "마르기노케팔리아"
    ],

    "백악기": [
        "스피노사우루스", "카르카로돈토사우루스", "티라노사우루스",
        "유티라누스", "딜롱", "알렉트로사우루스",
        "벨로키사우루스", "드로마이오사우루스", "데이노니쿠스",
        "오비랍토르", "테리지노사우루스", "오르니토미무스",
        "시노사우롭테릭스", "마시아카사우루스", "델타드로메우스",
        "노아사우루스", "기가노토사우루스", "수코미무스",
        "아마르가사우루스", "사우로포세이돈", "황허티탄",
        "후쿠이티탄", "에우헬로푸스", "펠로로사우루스",
        "아르젠티노사우루스", "파타고티탄", "우에르호사우루스",
        "파란토돈", "안타르크토펠타", "스테고우로스",
        "안킬로사우루스", "에드몬토니아", "이구아노돈",
        "우리노사우루스", "테논토사우루스", "무타부라사우루스",
        "레아엘리나사우라", "가스파리니사우라", "콴타사우루스",
        "아틀라스콥코사우루스", "에드몬토사우루스",
        "프시타코사우루스", "프로토케라톱스", "트리케라톱스",
        "아퀼롭스", "랴오케라톱스", "렙토케라톱스",
        "파키케팔로사우루스", "미크로파키케팔로사우루스",
        "스테노펠릭스"
    ]
}

# ==========================================
# 3. 공룡 분류 데이터
# ==========================================

CATEGORIES = {
    "수각류": [
        "헤레라사우루스", "스타우리코사우루스", "에오랍토르",
        "코엘로피시스", "릴리엔스테르누스", "프로콤프소그나투스",
        "세라토사우루스", "알로사우루스", "케라토사우루스",
        "딜로포사우루스", "메갈로사우루스", "토르보사우루스",
        "마르쇼사우루스", "콤프소그나투스", "오르니톨레스테스",
        "신랍토르", "양추아노사우루스", "모노로포사우루스",
        "크리올로포사우루스", "스피노사우루스",
        "카르카로돈토사우루스", "티라노사우루스", "유티라누스",
        "딜롱", "알렉트로사우루스", "벨로키사우루스",
        "드로마이오사우루스", "데이노니쿠스", "오비랍토르",
        "테리지노사우루스", "오르니토미무스", "시노사우롭테릭스",
        "마시아카사우루스", "델타드로메우스", "노아사우루스",
        "기가노토사우루스", "수코미무스"
    ],

    "용각류 및 근연 분류군": [
        "플라테오사우루스", "리오자사우루스", "무사우루스",
        "안키사우루스", "아파토사우루스", "브라키오사우루스",
        "디플로도쿠스", "카마라사우루스", "바로사우루스",
        "슈노사우루스", "마멘키사우루스", "슈퍼사우루스",
        "세이스모사우루스", "케티오사우루스", "투리아사우루스",
        "아마르가사우루스", "사우로포세이돈", "황허티탄",
        "후쿠이티탄", "에우헬로푸스", "펠로로사우루스",
        "아르젠티노사우루스", "파타고티탄"
    ],

    "검룡류": [
        "스테고사우루스", "켄트로사우루스",
        "화양고사우루스", "미라가이아",
        "우에르호사우루스", "파란토돈", "스테고우로스"
    ],

    "곡룡류": [
        "드라코펠타", "가고사우루스", "에우로펠타",
        "안타르크토펠타", "안킬로사우루스", "에드몬토니아"
    ],

    "조각류 및 기타 조반류": [
        "캄토사우루스", "드리오사우루스", "오스니엘리아",
        "헤테로돈토사우루스", "리코리누스",
        "아브릭토사우루스", "오트니엘로사우루스",
        "이구아노돈", "테논토사우루스", "무타부라사우루스",
        "레아엘리나사우라", "가스파리니사우라",
        "콴타사우루스", "아틀라스콥코사우루스",
        "에드몬토사우루스"
    ],

    "각룡류": [
        "프시타코사우루스", "프로토케라톱스",
        "트리케라톱스", "아퀼롭스",
        "랴오케라톱스", "렙토케라톱스"
    ],

    "후두류": [
        "파키케팔로사우루스",
        "미크로파키케팔로사우루스", "스테노펠릭스"
    ]
}

# 기타 선사시대 동물
OTHER_ANIMALS = {
    "익룡": [
        "에우디모르포돈", "프테로닥틸루스",
        "람포린쿠스", "프레온닥틸루스",
        "스카포그나투스"
    ],
    "해양 파충류": [
        "타니스트로페우스", "노토사우루스",
        "쇼니사우루스", "믹소사우루스",
        "심보스폰딜루스"
    ],
    "기타 고대 동물": [
        "포스토수쿠스", "리스트로사우루스"
    ]
}

# ==========================================
# 4. 이미지 가져오기
# ==========================================

@st.cache_data(ttl=86400, show_spinner=False)
def get_dinosaur_image(name):
    try:
        query = urllib.parse.urlencode({
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": name,
            "gsrnamespace": 0,
            "gsrlimit": 1,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 700
        })

        url = "https://ko.wikipedia.org/w/api.php?" + query

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "DinosaurDictionary/1.0"}
        )

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():
            return page.get("thumbnail", {}).get("source")

    except Exception:
        return None

    return None

# ==========================================
# 5. 디자인
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #101a17;
    color: #f3f5ee;
}

h1, h2, h3, p, label {
    color: #f3f5ee;
}

.dino-title {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    margin-top: 25px;
    color: #b7e4c7;
}

.dino-subtitle {
    text-align: center;
    color: #c1cec3;
    font-size: 17px;
    margin-bottom: 35px;
}

.dino-card {
    background: #20332b;
    border: 1px solid #456653;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 10px;
}

.dino-card h3 {
    color: #d4f2dc;
}

div.stButton > button {
    border-radius: 12px;
    border: 1px solid #719b7d;
    background-color: #294638;
    color: white;
    font-weight: bold;
    min-height: 48px;
}

div.stButton > button:hover {
    background-color: #477858;
    color: white;
    border-color: #b7e4c7;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 세부 정보 생성
# ==========================================

def get_category(name):
    for category, animals in CATEGORIES.items():
        if name in animals:
            return category

    for category, animals in OTHER_ANIMALS.items():
        if name in animals:
            return category

    if name == "마르기노케팔리아":
        return "조반류의 분류군"

    return "분류 확인 필요"


def get_food(name):
    if name in OTHER_ANIMALS.get("익룡", []):
        return "동물성 먹이를 먹었음"
    if name in OTHER_ANIMALS.get("해양 파충류", []):
        return "주로 물속의 동물을 먹었음"
    if name in OTHER_ANIMALS.get("기타 고대 동물", []):
        return "종에 따라 식성이 다름"

    category = get_category(name)

    if category == "수각류":
        if name in ["오비랍토르", "테리지노사우루스",
                    "오르니토미무스"]:
            return "잡식성 또는 식물성 먹이 섭취 가능성"
        return "육식성"

    if category in [
        "용각류 및 근연 분류군", "검룡류", "곡룡류",
        "조각류 및 기타 조반류", "각룡류", "후두류"
    ]:
        return "초식성"

    return "확인 필요"


def get_era_note(name, era):
    if name == "세라토사우루스":
        return "실제 생존 시기는 쥐라기입니다. 원래 보내준 목록의 트라이아스기 항목에 표시되어 있습니다."
    if name == "프테로닥틸루스":
        return "실제 생존 시기는 쥐라기 후기입니다."
    if name == "람포린쿠스":
        return "실제 생존 시기는 쥐라기 후기입니다."
    if name == "마르기노케팔리아":
        return "개별 공룡 속명이 아니라 각룡류와 후두류 등을 포함하는 분류군의 이름입니다."
    if name in OTHER_ANIMALS.get("익룡", []):
        return "공룡이 아닌 익룡입니다."
    if name in OTHER_ANIMALS.get("해양 파충류", []):
        return "공룡이 아닌 해양 파충류입니다."
    if name in OTHER_ANIMALS.get("기타 고대 동물", []):
        return "공룡이 아닌 다른 고대 파충류 또는 단궁류입니다."
    return "정확한 생존 시기는 종별 화석 기록에 따라 확인해야 합니다."


# ==========================================
# 7. 페이지 상태
# ==========================================

if "selected_era" not in st.session_state:
    st.session_state.selected_era = None

if "selected_dinosaur" not in st.session_state:
    st.session_state.selected_dinosaur = None


# ==========================================
# 8. 첫 화면
# ==========================================

def show_home():

    st.markdown(
        '<div class="dino-title">🦖 공룡 도감</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dino-subtitle">'
        '공룡들이 살았던 세상으로 떠나 보세요!'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # 세 시대 버튼을 화면 중앙에 일렬로 배치
    left, col1, col2, col3, right = st.columns(
        [1, 2, 2, 2, 1]
    )

    eras = [
        ("트라이아스기", "🦕", "약 2억 5200만~2억 100만 년 전"),
        ("쥐라기", "🦖", "약 2억 100만~1억 4500만 년 전"),
        ("백악기", "🦕", "약 1억 4500만~6600만 년 전")
    ]

    for col, (era, emoji, period) in zip(
        [col1, col2, col3], eras
    ):
        with col:
            st.markdown(
                f"""
                <div class="dino-card">
                    <h2 style="text-align:center;">{emoji}</h2>
                    <h3 style="text-align:center;">{era}</h3>
                    <p style="text-align:center;font-size:12px;">
                        {period}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                f"{era} 탐험하기",
                key=f"era_{era}",
                use_container_width=True
            ):
                st.session_state.selected_era = era
                st.session_state.selected_dinosaur = None
                st.rerun()

    st.write("")
    st.markdown(
        "<h3 style='text-align:center;'>"
        "세 시대의 다양한 고대 생물들을 만나 보세요!"
        "</h3>",
        unsafe_allow_html=True
    )


# ==========================================
# 9. 시대별 공룡 목록
# ==========================================

def show_era(era):

    if st.button("← 시대 선택으로 돌아가기"):
        st.session_state.selected_era = None
        st.session_state.selected_dinosaur = None
        st.rerun()

    st.markdown(
        f'<div class="dino-title">🦖 {era} 도감</div>',
        unsafe_allow_html=True
    )

    dinosaurs = DINOSAURS[era]

    st.write(f"총 {len(dinosaurs)}종의 목록")

    search = st.text_input(
        "🔍 공룡 이름 검색",
        placeholder="예: 티라노사우루스, 알로사우루스"
    )

    category_options = [
        "전체",
        "수각류",
        "용각류 및 근연 분류군",
        "검룡류",
        "곡룡류",
        "조각류 및 기타 조반류",
        "각룡류",
        "후두류",
        "익룡",
        "해양 파충류",
        "기타 고대 동물",
        "조반류의 분류군",
        "분류 확인 필요"
    ]

    selected_category = st.selectbox(
        "공룡 종류별 분류",
        category_options
    )

    filtered = []

    for name in dinosaurs:
        if search and search not in name:
            continue

        category = get_category(name)

        if selected_category != "전체":
            if category != selected_category:
                continue

        filtered.append(name)

    st.write(f"검색 결과: {len(filtered)}종")

    if not filtered:
        st.info("검색 결과가 없습니다.")
        return

    # 두 열로 공룡 카드 표시
    for i in range(0, len(filtered), 2):

        cols = st.columns(2)

        for j in range(2):
            if i + j >= len(filtered):
                break

            name = filtered[i + j]
            category = get_category(name)
            food = get_food(name)

            with cols[j]:
                st.markdown(
                    f"""
                    <div class="dino-card">
                        <h3>{name}</h3>
                        <p>분류: {category}</p>
                        <p>식성: {food}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    f"{name} 자세히 보기",
                    key=f"detail_{era}_{name}",
                    use_container_width=True
                ):
                    st.session_state.selected_dinosaur = name
                    st.rerun()


# ==========================================
# 10. 공룡 상세 도감
# ==========================================

def show_detail(name, era):

    if st.button("← 공룡 목록으로 돌아가기"):
        st.session_state.selected_dinosaur = None
        st.rerun()

    st.title(f"🦖 {name}")

    category = get_category(name)
    food = get_food(name)

    image_url = get_dinosaur_image(name)

    if image_url:
        st.image(
            image_url,
            caption=f"{name}",
            use_container_width=True
        )
    else:
        st.info(
            "대표 이미지를 자동으로 불러오지 못했습니다. "
            "공룡 이름을 검색해 이미지를 확인해 주세요."
        )

    st.subheader("📖 기본 정보")

    info1, info2 = st.columns(2)

    with info1:
        st.markdown("**목록에 수록된 시대**")
        st.write(era)

        st.markdown("**분류**")
        st.write(category)

    with info2:
        st.markdown("**식성**")
        st.write(food)

        st.markdown("**생물 종류**")
        if name in OTHER_ANIMALS.get("익룡", []):
            st.write("익룡")
        elif name in OTHER_ANIMALS.get("해양 파충류", []):
            st.write("해양 파충류")
        elif name in OTHER_ANIMALS.get("기타 고대 동물", []):
            st.write("기타 고대 동물")
        else:
            st.write("공룡 또는 관련 분류군")

    st.divider()

    st.subheader("🔎 생물학적 특징")

    st.write(
        f"{name}은(는) {category}에 해당하는 "
        f"생물입니다. 식성은 {food}으로 분류됩니다."
    )

    st.subheader("⚠️ 시대 및 분류 참고")

    st.write(get_era_note(name, era))

    st.caption(
        "※ 도감의 분류와 식성은 기본적인 안내 정보입니다. "
        "정확한 크기, 생존 시기 및 생태 정보는 "
        "해당 종의 화석 연구 자료를 추가로 확인해야 합니다."
    )

    wiki_query = urllib.parse.quote(name)

    st.link_button(
        "📚 더 자세한 정보 검색하기",
        f"https://ko.wikipedia.org/wiki/{wiki_query}"
    )


# ==========================================
# 11. 화면 실행
# ==========================================

if st.session_state.selected_era is None:

    show_home()

elif st.session_state.selected_dinosaur is not None:

    show_detail(
        st.session_state.selected_dinosaur,
        st.session_state.selected_era
    )

else:

    show_era(st.session_state.selected_era)

