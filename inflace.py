import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
import tools

import dotmap


def uvod():
    st.title("Kolik budu potřebovat měsíčně při průměrné inflaci ")

    st.markdown("""
        Tato kalkulačka ti pomůže odhadnout, kolik penez budes potrebovat na zivot pri prumerne inflaci

        ### Jak to funguje

        Zadáš:
        - **prumernou inflaci**
        - **Tvoje aktulani naklady na mesic**
        - **Pocet let do kdy chces vyhodnocovat graf**

        """)


def nacist_vstupy():
    v = dotmap.DotMap()

    v.naklady_na_zivot_mesicne = tools.input_money(
        "Naklady na mesic tveho zivota v aktualnich cenach", 50000
    )

    v.rocni_inflace = st.number_input(
        "Prumerna rocni inflace (% p.a.)", value=3.5) / 100

    v.do_kolika_let_vypocitat = st.number_input(
        "kolik let vyhodnocovat", min_value=1, value=50
    )

    v.mesicni_inflace = v.rocni_inflace / 12

    return v


def vypocet(vstupy):

    df = pd.DataFrame(columns=[
        # kolik ti je v danem roce
        "rok",
        "naklady_mesicne",
    ])
    df = df.set_index("rok")

    roky = list(
        range(1, vstupy.do_kolika_let_vypocitat + 1)
    )

    naklady_mesicne = vstupy.naklady_na_zivot_mesicne
    df.loc[0, "naklady_mesicne"] = naklady_mesicne
    for rok in roky:
        naklady_mesicne += naklady_mesicne * vstupy.rocni_inflace
        df.loc[rok, "naklady_mesicne"] = naklady_mesicne
        
    return df


def vykreslit_graf(vstupy, df):
    st.write("Graf vývoje nakladu podle inflace")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["naklady_mesicne"], 'k-', 
        label='Naklady na zivot mesicne'
    )

    ax.set_title('Graf vývoje nakladu podle inflace')
    ax.set_xlabel('Rok')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(tools.millions_formatter))
    #ax.set_xticks(roky)
    ax.set_xticks(df.index)
    if len(df) > 30:
        ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)


def vypsat_tabulku(vstupy, df):

    st.write("📊 Tabulka vývoje:")

    for col in [
        "naklady_mesicne",
    ]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)


def main():
    uvod()
    vstupy = nacist_vstupy()
    df = vypocet(vstupy)
    vykreslit_graf(vstupy, df)
    vypsat_tabulku(vstupy, df)

