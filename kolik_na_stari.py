
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd

# Zapnout wide layout
st.set_page_config(layout="wide")

# Funkce pro čitelné zadávání peněz
def input_money(label, default):
    raw = st.text_input(label, value=f"{default:,}".replace(",", " "), help="Zadej částku s oddělovači (např. 1 000 000)")
    cleaned = raw.replace(" ", "").replace(",", "")
    try:
        return int(cleaned)
    except ValueError:
        st.warning(f"Zadaná částka v poli '{label}' není číslo!")
        return 0

# Centrum stránky přes sloupce
col1, col2, col3 = st.columns([1, 3, 1])  # prostřední sloupec 2× širší

with col2:
    st.title("Kolik budu mít na stáří")

    st.markdown("""
        Tato kalkulačka ti pomůže odhadnout, jak se bude vyvíjet hodnota tvého majetku v průběhu života na základě několika základních údajů, které zadáš.

        ### Jak to funguje

        Zadáš:
        - **kolik ti je teď let**
        - **kolik máš aktuálně investováno**
        - **v jakém věku plánuješ přestat pracovat a začít čerpat úspory**
        - **měsíční náklady na život v dnešních cenách**
        - **očekávané roční zhodnocení investic (v %)**
        - **očekávanou průměrnou roční inflaci (v %)**

        Dokud **pracuješ**, kalkulace předpokládá, že se živíš sám a **nečerpáš žádné peníze z investic**. Zároveň ale **už žádné další peníze do investic nepřidáváš** – investovaný kapitál pouze roste díky zadanému úroku.

        Jakmile dosáhneš zadaného věku odchodu z práce, začneš **čerpat peníze na život z investic**. Výdaje na život se přepočítávají na roční bázi a **každý rok rostou podle zadané inflace**.

        Na výstupu uvidíš:
        - **graf vývoje majetku** až do věku 95 let
        - **tabulku** s přehledem kapitálu, úroků a výdajů v každém roce

        """)


    kolik_ti_je = st.number_input("Aktuální věk - kolik ti ted je", min_value=1, value=30)
    v_kolika_prestanes_pracovat = st.number_input("V kolika letech planujes prestat pracovat a zacnes zit z majetku", min_value=1, value=60)
    do_kolika_let_vypocitat = 95

    naklad_na_zivot_mesicne = input_money("Naklady na mesic tveho zivota v aktualnich cenach", 50000)
    vstupni_kapital = input_money("Tvuj aktualni kapital v investicich", 1_000_000)

    rocni_inflace = st.number_input("Prumerna rocni inflace (% p.a.)", value=3.5) / 100
    uroceni_kapitalu = st.number_input("Rocni urok na kapitalu (% p.a.)", value=7.0) / 100

    st.write("👇 Graf vývoje majetku:")

    # Formátování osy Y
    def millions_formatter(x, pos):
        if x >= 1e6:
            return f'{x/1e6:.0f}M'
        elif x >= 1e3:
            return f'{x/1e3:.0f}K'
        else:
            return f'{x:.0f}'

    naklad_na_zivot_v_letech_mesicne = []
    naklad_na_zivot_v_letech_rocne = []
    kapital = vstupni_kapital
    kapital_v_letech = []
    uroky_kapitalu_v_letech = []

    roky = list(range(kolik_ti_je, do_kolika_let_vypocitat + 1))
    for rok in roky:
        naklad_na_zivot_v_letech_mesicne.append(naklad_na_zivot_mesicne)
        rocni_naklad = naklad_na_zivot_mesicne * 12
        naklad_na_zivot_v_letech_rocne.append(rocni_naklad)
        naklad_na_zivot_mesicne *= (1 + rocni_inflace)

        if rok >= (v_kolika_prestanes_pracovat + 1):
            kapital -= rocni_naklad
            if kapital <= 0:
                kapital = 0

        urok_na_kapitalu = kapital * uroceni_kapitalu
        kapital += urok_na_kapitalu
        kapital_v_letech.append(kapital)
        uroky_kapitalu_v_letech.append(urok_na_kapitalu)

    # Graf
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(roky, naklad_na_zivot_v_letech_mesicne, 'c--', label='Naklady na zivot mesicne')
    ax.plot(roky, naklad_na_zivot_v_letech_rocne, 'c', label=f'Naklady na zivot rocne, inflace {(rocni_inflace * 100):.2f}% p.a.')
    ax.plot(roky, kapital_v_letech, 'b', label=f'Hodnota kapitalu (start {millions_formatter(vstupni_kapital, None)})', linewidth=1)
    ax.plot(roky, uroky_kapitalu_v_letech, 'b--', label=f'Uroky na kapitalu {(uroceni_kapitalu * 100):.2f}% p.a.', linewidth=1)

    ax.axvline(x=v_kolika_prestanes_pracovat, color='red', linestyle='--', linewidth=2)

    ax.set_title('Vypocet vlastniho duchodu')
    ax.set_xlabel('Rok')
    ax.set_ylabel('Hodnoty [Kč]')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))
    ax.set_xticks(roky)
    ax.xaxis.set_major_locator(MultipleLocator(2))

    ax.legend()
    fig.tight_layout()

    st.pyplot(fig)

    # Tabulka
    df = pd.DataFrame({
        "Věk": roky,
        "Kapital": kapital_v_letech,
        "Urok z kapitalu": uroky_kapitalu_v_letech,
        "Naklady rocne": naklad_na_zivot_v_letech_rocne,
    })

    st.write("📊 Tabulka vývoje:")
    st.dataframe(df)
