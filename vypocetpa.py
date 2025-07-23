import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
import tools

import dotmap


def uvod():
    st.title("Jake je prumerne zhodnoceni moji investice")

    st.markdown("""
        
        """)


def nacist_vstupy():
    v = dotmap.DotMap()

    v.vstupni_castka = tools.input_money(
        "Vlozena částka Kč", 50000
    )

    v.aktualni_hodnota = tools.input_money(
        "Aktualni hodnota Kč", 65000
    )

    v.delka_investice = st.number_input(
        "Délka investice let", min_value=0.1, value=2.0, step=0.1
    )

    return v


def vypocet(vstupy):

    if vstupy.vstupni_castka <= 0 or vstupy.delka_investice <= 0:
        raise ValueError("Initial investment and time period must be greater than 0.")
    
    rate = (vstupy.aktualni_hodnota / vstupy.vstupni_castka) ** (1 / vstupy.delka_investice) - 1

    return rate


def popis_vysledku(hodnota):
    p = hodnota * 100
    st.markdown(f"""

### Výsledek
**Prumerne zhodnoceni Tvoji investice je {p:.2f} % p.a.**
"""
    )


def main():
    uvod()
    vstupy = nacist_vstupy()
    vysledna_hodnota = vypocet(vstupy)
    popis_vysledku(vysledna_hodnota)

