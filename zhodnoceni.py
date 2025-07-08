import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
import tools

import dotmap


def uvod():
    st.title("Kolik budu mit kdyz se moje investovana castka zhodnoti ")

    st.markdown("""
        Tato kalkulačka ti pomůže odhadnout, kolik penez budes mit kdyz se tvoje investice bude zhodnocovat urokem % p.a. Kalkulacka predpoklada ze se uroky pripisuji k investici mesicne.

        ### Jak to funguje

        Zadáš:
        - **velikost investice**
        - **rocni zhodnoceni % p.a.**
        - **Delka investice (pocet let)**

        """)


def nacist_vstupy():
    v = dotmap.DotMap()

    v.investice = tools.input_money(
        "Naklady na mesic tveho zivota v aktualnich cenach", 50000
    )

    v.rocni_zhodnoceni = st.number_input(
        "Prumerne rocni zhodnoceni (% p.a.)", value=8) / 100

    v.delka_investice = st.number_input(
        "Delka investice v letech", min_value=1, value=10
    )

    return v


def vypocet(vstupy):

    df = pd.DataFrame(columns=[
        # kolik ti je v danem roce
        "rok",
        "hodnota_investice",
    ])
    df = df.set_index("rok")

    roky = list(
        range(1, vstupy.delka_investice + 1)
    )

    hodnota_investice = vstupy.investice
    df.loc[0, "hodnota_investice"] = hodnota_investice

    for rok in roky:
        for i in range(12):
            hodnota_investice += hodnota_investice * (vstupy.rocni_zhodnoceni / 12)
        df.loc[rok, "hodnota_investice"] = hodnota_investice
        
    return df


def vykreslit_graf(vstupy, df):
    st.write("Graf vývoje hodnoty investice")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["hodnota_investice"], 'k-', 
        label='Hodnota investice'
    )

    ax.set_title('Graf vývoje hodnoty investice')
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
        "hodnota_investice",
    ]:
        df[col] = df[col].map(lambda x: f"{x:,.0f} Kč".replace(",", " "))

    st.table(df)


def main():
    uvod()
    vstupy = nacist_vstupy()
    df = vypocet(vstupy)
    vykreslit_graf(vstupy, df)
    vypsat_tabulku(vstupy, df)

