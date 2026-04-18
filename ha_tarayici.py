import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

st.set_page_config(page_title="HA Al Sinyali Tarayıcı", page_icon="📡", layout="wide")

BIST100 = [
    "ACSEL","ADEL","ADESE","AEFES","AGESA","AGROT","AHGAZ","AKBNK","AKCNS","AKFEN",
    "AKGRT","AKMGY","AKSA","AKSEN","AKSGY","AKSUE","AKTAE","ALARK","ALBRK","ALFAS",
    "ALGYO","ALKIM","ALTNY","ANELE","ANGEN","ANHYT","ANSGR","ARASE","ARCLK","ARDYZ",
    "ARENA","ARSAN","ASELS","ASGYO","ASTOR","ATAGY","ATAKP","ATATP","ATEKS","AVGYO",
    "AVOD","AYDEM","AYEN","AYGAZ","AZTEK","BAGFS","BAKAB","BANVT","BERA","BFREN",
    "BIENY","BIGCH","BIMAS","BIZIM","BJKAS","BLCYT","BMEKS","BOSSA","BRISA","BRKSN",
    "BRKVY","BRSAN","BRYAT","BSOKE","BTCIM","BUCIM","BURCE","BURVA","BVSAN","CANTE",
    "CCOLA","CEMAS","CEMTS","CIMSA","CLEBI","CMBTN","CMENT","CONSE","COSMO","CRFSA",
    "CUSAN","CWENE","DAGI","DAPGM","DENGE","DGNMO","DITAS","DOAS","DOCO","DOGUB",
    "DPENS","DRDOC","DTRND","DURAN","DYOBY","DZGYO","ECILC","ECZYT","EDIP","EGEEN",
    "EGGUB","EGPRO","EGSER","EKGYO","EKSUN","ELITE","EMKEL","EMNIS","ENERY","ENJSA",
    "ENKAI","ENSRI","ENTEK","EPLAS","ERBOS","EREGL","ERSU","ESCAR","ESCOM","ESEN",
    "ETILR","EUREN","EUPWR","EYGYO","FENER","FLAP","FMIZP","FONET","FORMT","FORTE",
    "FROTO","GARAN","GARFA","GEDIK","GEDZA","GENTS","GEREL","GESAN","GILDI","GLYHO",
    "GLRYH","GLYHO","GOKNR","GOLTS","GOODY","GOZDE","GRNYO","GRSEL","GSDDE","GSDHO",
    "GSRAY","GUBRF","GWIND","GZNMI","HALKB","HATEK","HEKTS","HKTM","HLGYO","HMTEK",
    "HURGZ","ICBCT","IDGYO","IEYHO","IHAAS","IHEVA","IHGZT","IHLAS","IHLGM","IHYAY",
    "IMASM","INDES","INFO","INTEM","INVEO","IPEKE","ISDMR","ISFIN","ISGSY","ISGYO",
    "ISMEN","ISYAT","ITTFK","IZFAS","IZINV","IZMDC","IZOCM","JANTS","KAYSE","KCAER",
    "KENT","KERVN","KERVT","KFEIN","KGYO","KLGYO","KLKIM","KLMSN","KLNMA","KLRHO",
    "KMPUR","KNFRT","KONYA","KORDS","KOZAA","KOZAL","KRDMA","KRDMB","KRDMD","KRONT",
    "KSTUR","KTLEV","KTSKR","KUTPO","KUVVA","KUYAS","LIDER","LIDFA","LINK","LKMNH",
    "LOGO","LRSHO","LUKSK","MAALT","MACKO","MAGEN","MAKIM","MAKTK","MAVI","MEDTR",
    "MEGAP","MEPET","MERCN","MERIT","MERKO","METRO","METUR","MGROS","MIPAZ","MNDRS",
    "MNDTR","MOBTL","MPARK","MRGYO","MRSHL","MSGYO","MTRKS","MZHLD","NATEN","NETAS",
    "NIBAS","NTGAZ","NTHOL","NUGYO","NUHCM","OBASE","ODAS","ODINE","OFSYM","ONCSM",
    "ORCAY","ORGE","ORMA","OSMEN","OSTIM","OTKAR","OTTO","OYAKC","OYAYO","OYLUM",
    "OYYAT","OZGYO","OZKGY","PAPIL","PARSN","PCILT","PEHOL","PEKGY","PENGD","PENTA",
    "PETKM","PGSUS","PINSU","PKART","PKENT","PLTUR","PNLSN","POLHO","POLTK","PRKAB",
    "PRKME","PRZMA","PSDTC","PTOFS","QUAGR","RALYH","RAYSG","RHEAG","RNPOL","RODRG",
    "ROYAL","RTALB","RUBNS","RYSAS","SAFKR","SAHOL","SANFM","SANKO","SARKY","SASA",
    "SAYAS","SDTTR","SEGYO","SEKFK","SEKUR","SELEC","SELGD","SELVA","SEYKM","SILVR",
    "SISE","SKBNK","SKYLP","SMART","SNGYO","SNICA","SODSN","SOKM","SONME","SRVGY",
    "SUMAS","SUNTK","SUWEN","TABGD","TARKM","TATEN","TAVHL","TBORG","TCELL","TDGYO",
    "TEKTU","TERA","TETMT","TGSAS","THYAO","TIRE","TKFEN","TKNSA","TLMAN","TMSN",
    "TNZTP","TOASO","TRCAS","TRGYO","TRILC","TSPOR","TTKOM","TTRAK","TUCLK","TUCSY",
    "TUKAS","TUPRS","TUREX","TURGG","TURSG","TZNGY","UAVK","ULAS","ULKER","ULUFA",
    "ULUSE","ULUUN","UMRAF","UNLU","USAK","VAKBN","VAKFN","VAKKO","VBTS","VERUS",
    "VESBE","VESTL","VKGYO","VKFYO","WNDMR","XFABD","XTRZM","YBTAS","YEOTK","YESIL",
    "YGGYO","YGYO","YKSLN","YUNSA","ZEDUR","ZOREN","ZRGYO",
]

BIST100_TEMIZ = sorted(list(set(BIST100)))[:100]


def hesapla_ha(df):
    ha_close = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4

    ha_open = np.zeros(len(df))
    ha_open[0] = (df["Open"].iloc[0] + df["Close"].iloc[0]) / 2
    for i in range(1, len(df)):
        ha_open[i] = (ha_open[i-1] + ha_close.iloc[i-1]) / 2

    ha_open_s = pd.Series(ha_open, index=df.index)
    ha_high = pd.concat([df["High"], ha_open_s, ha_close], axis=1).max(axis=1)
    ha_low  = pd.concat([df["Low"],  ha_open_s, ha_close], axis=1).min(axis=1)

    ha = pd.DataFrame({
        "HA_Open":  ha_open_s,
        "HA_High":  ha_high,
        "HA_Low":   ha_low,
        "HA_Close": ha_close,
    }, index=df.index)
    return ha


def sinyal_tespit(ha):
    """
    Al sinyali kuralları:
    - n-2: kırmızı mum (düşüş trendi teyidi)
    - n-1: doji (küçük gövde, her iki yanda fitil)
    - n  : yeşil mum + alt fitil yok veya çok küçük
    """
    if len(ha) < 3:
        return None

    n = len(ha) - 1
    gun = ha.iloc[n]
    onceki = ha.iloc[n-1]
    onceki2 = ha.iloc[n-2]

    # Mevcut mum hesaplamaları
    gun_govde     = abs(gun["HA_Close"] - gun["HA_Open"])
    gun_alt_fitil = abs(min(gun["HA_Open"], gun["HA_Close"]) - gun["HA_Low"])
    gun_ust_fitil = abs(gun["HA_High"] - max(gun["HA_Open"], gun["HA_Close"]))

    # Önceki mum (doji kontrolü)
    onc_govde     = abs(onceki["HA_Close"] - onceki["HA_Open"])
    onc_alt_fitil = abs(min(onceki["HA_Open"], onceki["HA_Close"]) - onceki["HA_Low"])
    onc_ust_fitil = abs(onceki["HA_High"] - max(onceki["HA_Open"], onceki["HA_Close"]))
    onc_toplam    = onc_govde + onc_alt_fitil + onc_ust_fitil

    # Önceki2 mum (düşüş teyidi)
    onc2_kirmizi = onceki2["HA_Close"] < onceki2["HA_Open"]

    # Kurallar
    gun_yesil    = gun["HA_Close"] > gun["HA_Open"]
    alt_fitil_yok = gun_alt_fitil < gun_govde * 0.2  # alt fitil gövdenin %20'sinden az
    doji_mu      = (onc_govde < onc_toplam * 0.35) and (onc_alt_fitil > onc_govde * 0.1) and (onc_ust_fitil > onc_govde * 0.1)

    # Sinyal gücü skoru (0-100)
    skor = 0
    detay = []

    if gun_yesil:
        skor += 30
        detay.append("Yeşil mum")
    if alt_fitil_yok:
        skor += 30
        detay.append("Alt fitil yok")
    if doji_mu:
        skor += 25
        detay.append("Önceki doji")
    if onc2_kirmizi:
        skor += 15
        detay.append("Düşüş teyidi")

    if skor >= 55:  # en az yeşil + bir kural daha
        return {
            "skor": skor,
            "detay": " | ".join(detay),
            "ha_close": round(gun["HA_Close"], 2),
            "ha_open": round(gun["HA_Open"], 2),
            "alt_fitil": round(gun_alt_fitil, 3),
            "doji": doji_mu,
        }
    return None


def ha_trend_durumu(ha):
    """Son mumun genel HA trend durumunu döndür"""
    gun = ha.iloc[-1]
    govde = abs(gun["HA_Close"] - gun["HA_Open"])
    alt   = abs(min(gun["HA_Open"], gun["HA_Close"]) - gun["HA_Low"])
    ust   = abs(gun["HA_High"] - max(gun["HA_Open"], gun["HA_Close"]))

    if gun["HA_Close"] > gun["HA_Open"] and alt < govde * 0.2:
        return "Güçlü Yükseliş"
    elif gun["HA_Close"] > gun["HA_Open"]:
        return "Yükseliş"
    elif govde < (alt + ust) * 0.35:
        return "Doji / Kararsız"
    elif gun["HA_Close"] < gun["HA_Open"] and ust < govde * 0.2:
        return "Güçlü Düşüş"
    else:
        return "Düşüş"


@st.cache_data(ttl=1800, show_spinner=False)
def veri_cek(sembol, period="6mo"):
    try:
        ticker = sembol + ".IS"
        df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 10:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close"]].dropna()
        return df
    except:
        return None


def tara(semboller, period, ilerleme_bar, durum_yazisi):
    sonuclar = []
    toplam = len(semboller)

    for i, sembol in enumerate(semboller):
        durum_yazisi.text(f"Tarıyor: {sembol} ({i+1}/{toplam})")
        ilerleme_bar.progress((i+1) / toplam)

        df = veri_cek(sembol, period)
        if df is None:
            time.sleep(0.05)
            continue

        try:
            ha = hesapla_ha(df)
            sinyal = sinyal_tespit(ha)
            trend  = ha_trend_durumu(ha)
            gercek_close = round(float(df["Close"].iloc[-1]), 2)

            sonuc = {
                "Sembol": sembol,
                "Son Fiyat (₺)": gercek_close,
                "HA Trend": trend,
                "AL Sinyali": "✅ VAR" if sinyal else "—",
                "Sinyal Skoru": sinyal["skor"] if sinyal else 0,
                "Sinyal Detay": sinyal["detay"] if sinyal else "",
                "_sinyal": sinyal is not None,
            }
            sonuclar.append(sonuc)
        except:
            pass

        time.sleep(0.08)

    return pd.DataFrame(sonuclar)


# ─── ARAYÜZ ───────────────────────────────────────────────────────────────────

st.title("📡 Heikin Ashi — Al Sinyali Tarayıcı")
st.caption("BIST hisselerinde Doji + Yeşil Mum al sinyalini otomatik tespit eder.")

with st.sidebar:
    st.header("Ayarlar")

    period = st.selectbox(
        "Veri periyodu",
        ["3mo", "6mo", "1y"],
        index=1,
        format_func=lambda x: {"3mo":"3 Ay","6mo":"6 Ay","1y":"1 Yıl"}[x]
    )

    st.markdown("---")
    st.markdown("**Al Sinyali Kriterleri**")
    st.markdown("""
- Son mum **yeşil** (HA Close > HA Open)
- Alt fitil **yok veya çok küçük** (< gövde %20)
- Önceki mum **doji** benzeri
- Önceki2 mum **kırmızı** (trend teyidi)

Sinyal skoru ≥ 55 olan hisseler listelenir.
""")

    st.markdown("---")
    min_skor = st.slider("Min. sinyal skoru", 55, 100, 70, step=5)

    tara_btn = st.button("Taramayı Başlat", type="primary", use_container_width=True)

# Ana alan
if tara_btn:
    st.info(f"BIST100 tarıyor — {len(BIST100_TEMIZ)} hisse, bu işlem 2-3 dakika sürebilir...")

    prog = st.progress(0)
    durum = st.empty()

    df_sonuc = tara(BIST100_TEMIZ, period, prog, durum)

    durum.empty()
    prog.empty()

    st.session_state["df_sonuc"] = df_sonuc
    st.session_state["tarama_zamani"] = datetime.now().strftime("%d.%m.%Y %H:%M")

if "df_sonuc" in st.session_state:
    df = st.session_state["df_sonuc"].copy()
    zaman = st.session_state.get("tarama_zamani","")

    st.caption(f"Son tarama: {zaman}")

    # Özet metrikler
    toplam = len(df)
    sinyalli = df["_sinyal"].sum()
    guclu = (df["Sinyal Skoru"] >= 85).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Taranan Hisse", toplam)
    c2.metric("Al Sinyali", sinyalli)
    c3.metric("Güçlü Sinyal (≥85)", guclu)
    c4.metric("Sinyal Oranı", f"%{round(sinyalli/toplam*100,1) if toplam else 0}")

    st.markdown("---")

    # Filtreler
    col1, col2 = st.columns([3,1])
    with col1:
        filtre = st.radio(
            "Göster:",
            ["Sadece al sinyali olanlar", "Tüm hisseler"],
            horizontal=True
        )
    with col2:
        trend_filtre = st.multiselect(
            "HA Trend Filtresi",
            ["Güçlü Yükseliş","Yükseliş","Doji / Kararsız","Düşüş","Güçlü Düşüş"],
            default=[]
        )

    # Uygula
    df_goster = df.copy()
    if filtre == "Sadece al sinyali olanlar":
        df_goster = df_goster[df_goster["_sinyal"]]
    if trend_filtre:
        df_goster = df_goster[df_goster["HA Trend"].isin(trend_filtre)]
    df_goster = df_goster[df_goster["Sinyal Skoru"] >= min_skor]
    df_goster = df_goster.sort_values("Sinyal Skoru", ascending=False)

    gorunur = df_goster.drop(columns=["_sinyal"])

    if gorunur.empty:
        st.warning("Seçilen kriterlere uyan hisse bulunamadı.")
    else:
        st.dataframe(
            gorunur.style.apply(
                lambda row: ["background-color: rgba(29,158,117,0.15)" if row["AL Sinyali"] == "✅ VAR" else "" for _ in row],
                axis=1
            ).format({"Sinyal Skoru": "{:.0f}", "Son Fiyat (₺)": "{:.2f}"}),
            use_container_width=True,
            hide_index=True,
            height=min(600, 40 + len(gorunur) * 36),
        )

        csv = gorunur.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "CSV İndir",
            data=csv,
            file_name=f"ha_sinyaller_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

else:
    st.markdown("""
    ### Nasıl kullanılır?
    1. Sol panelden veri periyodunu seç
    2. **Taramayı Başlat** butonuna tıkla
    3. Tarama bittikten sonra al sinyali olan hisseler tabloda görünür
    4. Sinyal skoruna ve HA trend durumuna göre filtrele
    """)
