import streamlit as st
from streamlit_js_eval import streamlit_js_eval

import nezavislost
import splatkovy_uver_investice
import inflace
import zhodnoceni
import standard
import vypocetpa


if 'page' not in st.session_state:
    st.session_state.page = 'home'

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()

def kalkulacka_radek(nazev, popis, klic):
    with st.container(border=True):

        # Vykresli obsah
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(nazev, key=klic):
                navigate(klic)
        with col2:
            st.markdown(f"**{popis}**")

def show_home():
    with open("uvod.txt", "r", encoding="utf-8") as file:
        uvod_text = file.read()
        st.markdown(uvod_text)

    st.write("Vyber si kalkulačku:")

    kalkulacka_radek("📈 Financni nezavislost", "Spočítej si svoji financni nezavislost", "nezavislost")
    kalkulacka_radek("💰 Splatkovy uver na investovani", "Vyplati se pujcit si splatkovy uver a investovat?", "splatkovy_uver_investice")
    kalkulacka_radek("Naklady podle inflace", "Kolik budu potrebovat pri inflaci?", "inflace")
    kalkulacka_radek("Hodnota investice", "Zjisti, jakou hodnotu bude mít Tvoje investovaná částka při zvolené výši procentuálního zhodnocení a po uplynutí Tvého investičního horizontu.", "zhodnoceni")
    kalkulacka_radek("Velikost portfolio", "Jak velke portfolio potrebuji abych si udrzel zivotni standard?", "standard")
    kalkulacka_radek("Vypocet uroku p.a.", "Jake je prumerne zhodnoceni moji investice za rok?", "vypocetpa")

def show_jina():
    st.title("🛠️ Jiná kalkulačka")
    st.write("Tady bude jiná kalkulačka.")

def load_page_width():
    return streamlit_js_eval(js_expressions="window.innerWidth", key="width_check")

def content():
    st.set_page_config(layout="wide")
    if 'width' not in st.session_state:
        width = load_page_width()
        if width is not None:
            st.session_state.width = width
    else:
        width = st.session_state.width

    if width is not None and width > 1024:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            content_handler()
    else:
        content_handler()

def content_handler():
    global pages

    if not st.session_state.page in pages:
        st.session_state.page = 'home'
    handler = pages[st.session_state.page]
    is_home = st.session_state.page == 'home'
    if not is_home:
        if st.button("⬅️ Zpět na úvod"):
            navigate('home')
    handler()



default_page = "home"
pages = {
    'home': show_home,
    'nezavislost': nezavislost.main,
    'splatkovy_uver_investice': splatkovy_uver_investice.main,
    'inflace': inflace.main,
    'zhodnoceni': zhodnoceni.main,
    'standard': standard.main,
    'vypocetpa': vypocetpa.main,
}


params = st.query_params
if "s" in params:
    s_value = params["s"]
    if s_value in pages:
        st.session_state.page = s_value

    st.query_params.clear()
    st.rerun()


content()
