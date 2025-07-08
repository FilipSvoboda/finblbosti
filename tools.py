
import streamlit as st
import re

# Formátování osy Y
def millions_formatter(x, pos):
    if x >= 1e6:
        return f'{x/1e6:.0f}M'
    elif x >= 1e3:
        return f'{x/1e3:.0f}K'
    else:
        return f'{x:.0f}'

# Funkce pro čitelné zadávání peněz
def input_money(label, default=0):
    raw = st.text_input(label, value=f"{default:,}".replace(",", " "), 
            help="Zadej částku s oddělovači (např. 1 000 000)"
          )
    cleaned = raw.replace(" ", "").replace(",", "")
    try:
        return int(cleaned)
    except ValueError:
        st.warning(f"Zadaná částka v poli '{label}' není číslo!")
        return 0


