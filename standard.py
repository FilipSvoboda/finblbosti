import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
import tools

import dotmap


def uvod():
    st.title("K jaké finální sumě se chci investováním dostat, aby byl zachován můj životní standard?")

    st.markdown("""
        Tato kalkulačka ti pomůže odhadnout, kolik potrebujes mit zainvestovano abys mohl vybirat urcitou cast investice a byl zachovany tvuj zivotni standard s prihlednutim k inflaci.

        ### Jak to funguje

        Zadáš:
        - **kolik procent z portfolia chces rocne vybirat**
        - **Tvoje naklady mesicne**
        - **prumerna rocni inflace % p.a.**
        - **jak dlouho vyhodnocovat graf**
        """)


def nacist_vstupy():
    v = dotmap.DotMap()

    v.vybirat_procent = st.number_input(
        "Kolik % z portfolia rocne chces vybirat (%)", value=4) / 100

    v.naklady = tools.input_money(
        "Naklady na mesic tveho zivota v aktualnich cenach", 50000
    )

    v.rocni_inflace = st.number_input(
        "Prumerna rocni inflace (% p.a.)", value=3.5) / 100

    v.vyhodnocovat_let = st.number_input(
        "Jak dlouho vyhodnocovat graf", min_value=1, value=30
    )

    return v


def vypocet(vstupy):

    df = pd.DataFrame(columns=[
        # kolik ti je v danem roce
        "rok",
        "naklady",
        "nutne_portfolio",
    ])
    df = df.set_index("rok")

    roky = list(
        range(1, vstupy.vyhodnocovat_let + 1)
    )

    naklady = vstupy.naklady * 12
    df.loc[0, "naklady"] = naklady
    df.loc[0, "nutne_portfolio"] = naklady / vstupy.vybirat_procent

    for rok in roky:
        naklady += naklady * vstupy.rocni_inflace
        df.loc[rok, "naklady"] = naklady
        df.loc[rok, "nutne_portfolio"] = naklady / vstupy.vybirat_procent
        
    return df


def vykreslit_graf(vstupy, df):
    st.write("Jak velke portfolio potrebuji")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["naklady"], 'k-', 
        label='Naklady'
    )

    ax.plot(df.index, df["nutne_portfolio"], 'k-', 
        label='Nutne portfolio'
    )

    ax.set_title('Graf vývoje nutneho portfolia')
    ax.set_xlabel('Rok')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(tools.millions_formatter))
    ax.set_xticks(df.index)
    if len(df) > 30:
        ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)


def vypsat_tabulku(vstupy, df):

    st.write("📊 Tabulka vývoje:")

    for col in [
        "naklady",
        "nutne_portfolio",
    ]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)


def main():
    uvod()
    vstupy = nacist_vstupy()
    df = vypocet(vstupy)
    vykreslit_graf(vstupy, df)
    vypsat_tabulku(vstupy, df)

