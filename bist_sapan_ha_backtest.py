import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date
import plotly.graph_objects as go

st.set_page_config(
    page_title="BIST Sapan + Heikin Ashi Backtest",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e2433;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #8b95a8; margin-bottom: 4px; }
    .metric-value { font-size: 24px; font-weight: 700; }
    .metric-pos { color: #22c55e; }
    .metric-neg { color: #ef4444; }
    .metric-neu { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ─── HİSSE LİSTELERİ ──────────────────────────────────────────────────────────
# Sapan Stratejisi backtest sonuçlarına göre en iyi 50 hisse (2022-2026)
TOP50 = {
    "BURCE","BURVA","GRTHO","PASEU","CRDFA","BYDNR","BAHKM","BMSCH","AKSUE","ARSAN",
    "AKYHO","BRSAN","HEDEF","ISGSY","ICUGS","CRFSA","AVTUR","AKSA","KRGYO","BIGCH",
    "BRKVY","ETYAT","BORLS","BFREN","ULAS","AHGAZ","POLTK","BLCYT","BERA","KLRHO",
    "FLAP","OYAYO","DCTTR","IEYHO","ISKPL","CCOLA","GZNMI","KUVVA","HURGZ","ARENA",
    "RTALB","DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","TURGG","CVKMD","GUBRF",
}

# Telegram botundaki HISSELER listesi — birebir aynı (talimat gereği)
BIST_HISSELER = [
    "ACSEL","ADEL","ADESE","ADGYO","AFYON","AGHOL","AGESA","AGROT","AHSGY","AHGAZ",
    "AKYHO","AKENR","AKFGY","AKFIS","AKFYE","AKHAN","ATEKS","AKSGY","AKMGY","AKSA",
    "AKSEN","AKGRT","AKSUE","ALCAR","ALGYO","ALARK","ALBRK","ALCTL","ALFAS","ALKIM",
    "ALKA","AYCES","ALTNY","ALKLC","ALVES","ANSGR","AEFES","ANHYT","ASUZU","ANGEN",
    "ANELE","ARCLK","ARDYZ","ARENA","ARFYE","ARMGD","ARSAN","ARTMS","ARZUM","ASGYO",
    "ASELS","ASTOR","ATAGY","ATATR","ATAKP","AGYO","ATSYH","ATLAS","ATATP","AVOD",
    "AVGYO","AVTUR","AVHOL","AVPGY","AYDEM","AYEN","AYES","AYGAZ","AZTEK","A1CAP",
    "A1YEN","BAGFS","BAHKM","BAKAB","BALAT","BALSU","BNTAS","BANVT","BARMA","BASGZ",
    "BASCM","BEGYO","BTCIM","BSOKE","BYDNR","BAYRK","BERA","BRKSN","BESLR","BESTE",
    "BJKAS","BEYAZ","BIENY","BIGTK","BLCYT","BIMAS","BINBN","BIOEN","BRKVY","BRKO",
    "BIGEN","BRLSM","BRMEN","BIZIM","BLUME","BMSTL","BMSCH","BOBET","BORSK","BORLS",
    "BRSAN","BRYAT","BFREN","BOSSA","BRISA","BULGS","BURCE","BURVA","BUCIM","BVSAN",
    "BIGCH","CRFSA","CASA","CEMZY","CEOEM","CCOLA","CONSE","COSMO","CRDFA","CVKMD",
    "CWENE","CGCAM","CANTE","CATES","CLEBI","CELHA","CEMAS","CEMTS","CMBTN","CMENT",
    "CIMSA","CUSAN","DAGI","DAPGM","DARDL","DGATE","DCTTR","DMSAS","DENGE","DZGYO",
    "DERIM","DERHL","DESA","DESPC","DSTKF","DEVA","DNISI","DIRIT","DITAS","DMRGD",
    "DOCO","DOFRB","DOFER","DOHOL","DGNMO","ARASE","DOGUB","DGGYO","DOAS","DOKTA",
    "DURDO","DURKN","DUNYH","DYOBY","EBEBK","ECOGR","ECZYT","EDATA","EDIP","EFOR",
    "EGEEN","EGGUB","EGPRO","EGSER","EPLAS","EGEGY","ECILC","EKIZ","EKOS","EKSUN",
    "ELITE","EMKEL","EMNIS","EKGYO","EMPAE","ENDAE","ENJSA","ENERY","ENKAI","ENSRI",
    "ERBOS","ERCB","EREGL","KIMMR","ERSU","ESCAR","ESCOM","ESEN","ETILR","EUKYO",
    "EUYO","ETYAT","EUHOL","TEZOL","EUREN","EUPWR","EYGYO","FADE","FMIZP","FENER",
    "FLAP","FONET","FROTO","FORMT","FRMPL","FORTE","FRIGO","FZLGY","GWIND","GSRAY",
    "GARFA","GRNYO","GATEG","GEDIK","GEDZA","GLCVY","GENIL","GENTS","GENKM","GEREL",
    "GZNMI","GIPTA","GMTAS","GESAN","GLBMD","GLYHO","GOODY","GOKNR","GOLTS","GOZDE",
    "GRTHO","GSDDE","GSDHO","GUBRF","GLRYH","GLRMK","GUNDG","GRSEL","SAHOL","HLGYO",
    "HRKET","HATEK","HATSN","HDFGS","HEDEF","HEKTS","HKTM","HTTBT","HOROZ","HUBVC",
    "HUNER","HURGZ","ENTRA","ICBCT","ICUGS","INGRM","INVEO","INVES","ISKPL","IEYHO",
    "IDGYO","IHEVA","IHLGM","IHGZT","IHAAS","IHLAS","IHYAY","IMASM","INDES","INFO",
    "INTEK","INTEM","ISDMR","ISFIN","ISGYO","ISGSY","ISMEN","ISYAT","ISBIR","ISSEN",
    "IZINV","IZENR","IZMDC","IZFAS","JANTS","KFEIN","KLKIM","KLSER","KLYPV","KAPLM",
    "KRDMA","KRDMB","KRDMD","KAREL","KARSN","KRTEK","KARTN","KTLEV","KATMR","KAYSE",
    "KENT","KRVGD","KERVN","TCKRC","KZBGY","KLGYO","KLRHO","KMPUR","KLMSN","KCAER",
    "KCHOL","KOCMT","KLSYN","KNFRT","KONTR","KONYA","KONKA","KGYO","KORDS","KRPLS",
    "KOTON","KOPOL","KRGYO","KRSTL","KRONT","KSTUR","KUVVA","KUYAS","KBORU","KZGYO",
    "KUTPO","KTSKR","LIDER","LIDFA","LILAK","LMKDC","LINK","LOGO","LKMNH","LRSHO",
    "LUKSK","LYDHO","LYDYE","MACKO","MAKIM","MAKTK","MANAS","MAGEN","MARKA","MARMR",
    "MAALT","MRSHL","MRGYO","MARTI","MTRKS","MAVI","MZHLD","MEDTR","MEGMT","MEGAP",
    "MEKAG","MNDRS","MEPET","MERCN","MERIT","MERKO","METRO","MTRYO","MEYSU","MHRGY",
    "MIATK","MGROS","MSGYO","MPARK","MMCAS","MOBTL","MOGAN","MNDTR","MOPAS","EGEPO",
    "NATEN","NTGAZ","NTHOL","NETAS","NETCD","NIBAS","NUHCM","NUGYO","OBAMS","OBASE",
    "ODAS","ODINE","OFSYM","ONCSM","ONRYT","ORCAY","ORGE","ORMA","OSMEN","OSTIM",
    "OTKAR","OTTO","OYAKC","OYYAT","OYAYO","OYLUM","OZKGY","OZATD","OZGYO","OZRDN",
    "OZSUB","OZYSR","PAMEL","PNLSN","PAGYO","PAPIL","PRDGS","PRKME","PARSN","PASEU",
    "PSGYO","PAHOL","PATEK","PCILT","PGSUS","PEKGY","PENGD","PENTA","PSDTC","PETKM",
    "PKENT","PETUN","PINSU","PNSUT","PKART","PLTUR","POLHO","POLTK","PRZMA","RNPOL",
    "RALYH","RAYSG","REEDR","RYGYO","RYSAS","RODRG","ROYAL","RGYAS","RTALB","RUBNS",
    "RUZYE","SAFKR","SANEL","SNICA","SANFM","SANKO","SAMAT","SARKY","SASA","SVGYO",
    "SAYAS","SDTTR","SEGMN","SEKUR","SELEC","SELVA","SERNT","SRVGY","SEYKM","SILVR",
    "SNGYO","SKYLP","SMRTG","SMART","SODSN","SOKE","SKTAS","SONME","SNPAM","SUMAS",
    "SUNTK","SURGY","SUWEN","SMRVA","SEKFK","SEGYO","SKYMD","SKBNK","SOKM","TABGD",
    "TATGD","TATEN","TAVHL","TEKTU","TKFEN","TKNSA","TMPOL","TRHOL","TERA","TEHOL",
    "TGSAS","TOASO","TRGYO","TRMET","TRENJ","TLMAN","TSPOR","TDGYO","TSGYO","TUCLK",
    "TUKAS","TRCAS","TUREX","MARBL","TRILC","TCELL","TMSN","TUPRS","TRALT","THYAO",
    "PRKAB","TTKOM","TTRAK","TBORG","TURGG","GARAN","HALKB","ISATR","ISBTR","ISCTR",
    "ISKUR","KLNMA","TSKB","TURSG","SISE","VAKBN","UFUK","ULAS","ULUFA","ULUSE",
    "ULUUN","UMPAS","USAK","UCAYM","ULKER","UNLU","VAKFA","VAKFN","VKGYO","VKFYO",
    "VAKKO","VANGD","VBTYZ","VRGYO","VERUS","VERTU","VESBE","VESTL","VKING","VSNMD",
    "YKBNK","YAPRK","YATAS","YYLGD","YAYLA","YGGYO","YEOTK","YGYO","YYAPI","YESIL",
    "YBTAS","YIGIT","YONGA","YKSLN","YUNSA","ZGYO","ZEDUR","ZERGY","ZRGYO","ZOREN",
    "BINHO",
]

# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────
def squeeze(s):
    if hasattr(s, "squeeze"):
        s = s.squeeze()
    if hasattr(s, "iloc") and s.ndim == 2:
        s = s.iloc[:, 0]
    return s

def veri_cek(ticker, bas, bit):
    try:
        df = yf.download(ticker + ".IS", start=str(bas), end=str(bit),
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 50:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        for col in df.columns:
            df[col] = squeeze(df[col])
        df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return None

def endeks_filtre_olustur(bas, bit):
    try:
        df = yf.download("XU100.IS",
                         start=(bas - pd.DateOffset(years=1)).strftime("%Y-%m-%d"),
                         end=str(bit), interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            return {}
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = df.index.tz_localize(None)
        df["EMA200"] = squeeze(df["Close"]).ewm(span=200, adjust=False).mean()
        df.dropna(subset=["EMA200"], inplace=True)
        return {row.Index.date(): float(row.Close) > float(row.EMA200)
                for row in df.itertuples()}
    except Exception:
        return {}

# ─── İNDİKATÖRLER — bot/tarayıcı/backtest ile birebir aynı ───────────────────
def hesapla_ind(df):
    c = squeeze(df["Close"])
    h = squeeze(df["High"])
    l = squeeze(df["Low"])

    for p in [20, 50, 100, 200]:
        df[f"EMA{p}"] = c.ewm(span=p, adjust=False).mean()

    # ATR (14)
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    df["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).ewm(span=14, adjust=False).mean()

    # Stochastic (5,3,3) — tek smoothing, TradingView uyumlu
    lowest_low   = l.rolling(5).min()
    highest_high = h.rolling(5).max()
    stoch_k_raw  = 100 * (c - lowest_low) / (highest_high - lowest_low + 1e-10)
    k_smooth     = stoch_k_raw.rolling(3).mean()
    df["STOCH_K"] = k_smooth
    df["STOCH_D"] = k_smooth.rolling(3).mean()

    # MACD (50, 100, 9)
    ema_h = c.ewm(span=50,  adjust=False).mean()
    ema_y = c.ewm(span=100, adjust=False).mean()
    df["MACD"]     = ema_h - ema_y
    df["MACD_SIG"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_HIS"] = df["MACD"] - df["MACD_SIG"]

    return df

# ─── HEIKIN ASHI — ha_tarayici.py ile birebir aynı ──────────────────────────
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

def ha_skor_hesapla(ha, idx):
    """
    ha_tarayici.py'deki sinyal_tespit() skor mantığı — birebir aynı.
    idx = onay mumu (giriş günü) konumu. idx, idx-1, idx-2 kullanılır.
    Skor: yeşil mum +30, alt fitil yok +30, önceki doji +25, önceki2 kırmızı +15.
    Sinyal yoksa (idx < 2) None döner.
    """
    if idx < 2:
        return None, "", False

    gun     = ha.iloc[idx]
    onceki  = ha.iloc[idx-1]
    onceki2 = ha.iloc[idx-2]

    gun_govde     = abs(gun["HA_Close"] - gun["HA_Open"])
    gun_alt_fitil = abs(min(gun["HA_Open"], gun["HA_Close"]) - gun["HA_Low"])

    onc_govde     = abs(onceki["HA_Close"] - onceki["HA_Open"])
    onc_alt_fitil = abs(min(onceki["HA_Open"], onceki["HA_Close"]) - onceki["HA_Low"])
    onc_ust_fitil = abs(onceki["HA_High"] - max(onceki["HA_Open"], onceki["HA_Close"]))
    onc_toplam    = onc_govde + onc_alt_fitil + onc_ust_fitil

    onc2_kirmizi = onceki2["HA_Close"] < onceki2["HA_Open"]

    gun_yesil     = gun["HA_Close"] > gun["HA_Open"]
    alt_fitil_yok = gun_alt_fitil < gun_govde * 0.2
    doji_mu = (onc_govde < onc_toplam * 0.35) and \
              (onc_alt_fitil > onc_govde * 0.1) and \
              (onc_ust_fitil > onc_govde * 0.1)

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

    # ha_tarayici.py'de skor >= 55 "HA sinyali var" sayılıyor
    ha_sinyal_var = skor >= 55
    return skor, " | ".join(detay) if detay else "—", ha_sinyal_var

# ─── EMA DOKUNUŞ / HIGHER LOW — bot ile birebir aynı ────────────────────────
def ema_dokunusu_var_mi(low_val, high_val, ema20, ema50, ema100, ema200, tolerans):
    for ema_val in [ema20, ema50, ema100, ema200]:
        if pd.isna(ema_val):
            continue
        band_low  = ema_val * (1 - tolerans)
        band_high = ema_val * (1 + tolerans)
        if low_val <= band_high and high_val >= band_low:
            return True
    return False

def higher_low_kontrol(df, reversal_idx, lookback=30):
    if reversal_idx < 2:
        return True
    reversal_low = float(df["Low"].iloc[reversal_idx])
    sub = df["Low"].iloc[max(0, reversal_idx-lookback):reversal_idx]
    if len(sub) == 0:
        return True
    son_dip = float(sub.min())
    if reversal_low >= son_dip:
        return True
    for col in ["EMA100", "EMA200"]:
        if col in df.columns:
            ema_val = float(df[col].iloc[reversal_idx])
            if not pd.isna(ema_val) and reversal_low <= ema_val * 1.02:
                return True
    return False

# ─── SAPAN SİNYAL TESPİTİ (KAPANIŞ FİYATI — BOT İLE BİREBİR) ────────────────
def sapan_sinyal_uret(df, ha, sembol, ema_tolerans, zaman_stopu, atr_kat, rr_kat):
    """
    Sapan Stratejisi sinyali — Giriş: onay mumunun KAPANIŞ fiyatı (bot ile aynı).
    6 filtre bist_sapan_telegram_bot.py ile birebir aynı sırada ve eşiklerde.
    Her sinyale, onay mumunun HA verisinden hesaplanan 0-100 HA skoru eklenir.
    """
    sinyaller = []

    for i in range(2, len(df)):
        son        = df.iloc[i]      # onay mumu = giriş günü
        onceki     = df.iloc[i-1]    # dönüş mumu
        iki_onceki = df.iloc[i-2]

        # FİLTRE 1: EMA Trend
        if not (float(son["EMA20"]) > float(son["EMA50"]) >
                float(son["EMA100"]) > float(son["EMA200"])):
            continue

        # FİLTRE 2: Stochastic < 30 (dönüş mumunda)
        if float(onceki["STOCH_K"]) >= 30:
            continue

        # FİLTRE 3: MACD pozitif VEYA 5'ten az süredir negatif
        macd_vals    = df["MACD"].iloc[max(0, i-5):i]
        macd_pozitif = float(son["MACD"]) > 0
        negatif_sure = (macd_vals < 0).sum()
        if not macd_pozitif and negatif_sure >= 5:
            continue

        # FİLTRE 4: Onay mumu yeşil ve dönüş mumunun high'ını kırmış
        if float(son["Close"]) <= float(son["Open"]):
            continue
        if float(son["Close"]) <= float(onceki["High"]):
            continue

        # FİLTRE 5: EMA dokunuşu (dönüş mumunda)
        if not ema_dokunusu_var_mi(
            float(onceki["Low"]), float(onceki["High"]),
            float(onceki["EMA20"]), float(onceki["EMA50"]),
            float(onceki["EMA100"]), float(onceki["EMA200"]),
            tolerans=ema_tolerans
        ):
            continue

        # FİLTRE 6: Higher Low
        reversal_idx = i - 1
        if not higher_low_kontrol(df, reversal_idx):
            continue

        # GİRİŞ: onay mumunun kapanışı (bot ile birebir)
        giris   = float(son["Close"])
        atr_val = float(son["ATR"])
        stop    = round(giris - atr_kat * atr_val, 2)
        bir_r   = giris - stop
        if bir_r <= 0:
            continue
        hedef = round(giris + rr_kat * bir_r, 2)

        # HA skoru — onay mumunun (i) HA verisiyle hesaplanır
        ha_skor, ha_detay, ha_sinyal_var = ha_skor_hesapla(ha, i)
        if ha_skor is None:
            ha_skor, ha_detay, ha_sinyal_var = 0, "—", False

        sinyaller.append({
            "tarih"          : son.name,        # giriş günü = onay mumu günü
            "sembol"         : sembol,
            "giris"          : round(giris, 2),
            "stop"           : stop,
            "hedef"          : hedef,
            "bir_r"          : round(bir_r, 2),
            "top50"          : sembol in TOP50,
            "zaman_stopu_gun": zaman_stopu,
            "ha_skor"        : int(ha_skor),
            "ha_detay"       : ha_detay,
            "ha_sinyal_var"  : bool(ha_sinyal_var),
        })

    return sinyaller

# ─── HA SKOR DİLİMİ ──────────────────────────────────────────────────────────
def ha_dilim(skor):
    if skor < 25:
        return "0-25"
    elif skor < 50:
        return "25-50"
    elif skor < 75:
        return "50-75"
    else:
        return "75-100"

DILIM_SIRA = ["0-25", "25-50", "50-75", "75-100"]

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Backtest Ayarları")

st.sidebar.markdown("### 📅 Tarih Aralığı")
col1, col2 = st.sidebar.columns(2)
bas_tarih = col1.date_input("Başlangıç", value=date(2022, 1, 1),
                             min_value=date(2010, 1, 1), max_value=date.today())
bit_tarih = col2.date_input("Bitiş", value=date.today(),
                             min_value=date(2010, 1, 1), max_value=date.today())

st.sidebar.markdown("### 💰 Sermaye & Pozisyon")
portfoy      = st.sidebar.number_input("Başlangıç Sermaye (TL)", min_value=10000,
                                        max_value=100_000_000, value=1_000_000, step=10000)
max_pozisyon = st.sidebar.slider("Max Eş Zamanlı Pozisyon", 1, 20, 10, 1)
poz_yuzde    = st.sidebar.slider("Pozisyon Büyüklüğü (%)", 5.0, 50.0,
                                  round(100/max_pozisyon, 1), 5.0)

st.sidebar.markdown("### 📐 Strateji Parametreleri (bot ile aynı)")
ema_tolerans = st.sidebar.select_slider(
    "EMA Dokunuş Toleransı (%)", options=[1, 2, 3], value=2,
    help="Bot: %2"
) / 100
atr_kat = st.sidebar.select_slider(
    "ATR Katsayısı (Stop)", options=[1.0, 1.5, 2.0, 2.5, 3.0], value=1.5,
    help="Bot: 1.5"
)
rr_kat  = st.sidebar.select_slider(
    "R:R Katsayısı", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], value=1.5,
    help="Bot: 1.5"
)
zaman_stopu = st.sidebar.slider(
    "Zaman Stopu (gün)", 5, 40, 30, 1,
    help="Bot: 30 gün"
)

st.sidebar.markdown("### 🔍 Filtreler")
endeks_aktif = st.sidebar.checkbox("Endeks Filtresi (BIST100 > EMA200)", value=True)

st.sidebar.markdown("### 📡 HA Skorlama Katmanı")
ha_mod = st.sidebar.radio(
    "HA katmanı modu",
    ["Sadece etiketle (filtre yok)", "Eşik filtresi uygula"],
    help="'Sadece etiketle': tüm Sapan sinyalleri alınır, HA skoru yalnızca rapor için. "
         "'Eşik filtresi': HA skoru eşiğin altındaki sinyaller elenir."
)
ha_esik = st.sidebar.slider(
    "HA skor eşiği (filtre modunda)", 0, 100, 55, 5,
    help="ha_tarayici.py varsayılanı: 55"
)

# ─── BAŞLIK ───────────────────────────────────────────────────────────────────
st.title("📡 BIST Sapan + Heikin Ashi Skorlama Backtest")
st.caption(f"Giriş: Onay Mumu Kapanışı (bot ile birebir) | ATR Stop | R:R 1:{rr_kat} | "
           f"Zaman Stopu: {zaman_stopu} gün | HISSELER: Telegram botu listesi")

st.info(f"""
**Backtest Kuralları — Sapan Stratejisi (Kapanış Fiyatı, bot ile birebir):**
- Sinyal onay mumunun kapanışında tespit edilir, **giriş = onay mumu kapanışı**
- 6 filtre `bist_sapan_telegram_bot.py` ile birebir aynı
- Stop: Giriş − ATR(14) × {atr_kat} | Hedef: Giriş + (Giriş − Stop) × {rr_kat}
- Zaman stopu: **{zaman_stopu} gün** | Max **{max_pozisyon}** pozisyon | Pozisyon başı **%{poz_yuzde:.0f}**
- **HA skoru** her sinyale onay mumunun Heikin Ashi verisinden eklenir (`ha_tarayici.py` mantığı: yeşil +30, alt fitil yok +30, önceki doji +25, önceki2 kırmızı +15)
- HA modu: **{ha_mod}**{f" — eşik: {ha_esik}" if ha_mod.startswith("Eşik") else ""}
""")

# ─── BACKTEST ─────────────────────────────────────────────────────────────────
if st.button("🚀 Backtest Çalıştır", use_container_width=True, type="primary"):

    bas_ts   = pd.Timestamp(bas_tarih)
    bit_ts   = pd.Timestamp(bit_tarih)
    veri_bas = bas_ts - pd.DateOffset(years=1)
    veri_bit = bit_ts + pd.DateOffset(days=2)

    endeks_f = {}
    if endeks_aktif:
        with st.spinner("Endeks verisi indiriliyor..."):
            endeks_f = endeks_filtre_olustur(bas_ts, veri_bit)

    # Veri indir + indikatör + HA hesapla
    hisse_verileri = {}
    hisse_ha       = {}
    progress = st.progress(0, text="Veriler indiriliyor...")
    for hi, sembol in enumerate(BIST_HISSELER):
        progress.progress(
            (hi+1)/len(BIST_HISSELER),
            text=f"İndiriliyor: {sembol} ({hi+1}/{len(BIST_HISSELER)})"
        )
        df_raw = veri_cek(sembol,
                          veri_bas.to_pydatetime().date(),
                          veri_bit.to_pydatetime().date())
        if df_raw is None:
            continue
        try:
            ha = hesapla_ha(df_raw.copy())
            df = hesapla_ind(df_raw.copy())
            df.dropna(subset=["EMA200","STOCH_K","MACD","ATR"], inplace=True)
            if len(df) >= 50:
                hisse_verileri[sembol] = df
                # HA'yı df ile aynı indekse hizala
                hisse_ha[sembol] = ha.reindex(df.index)
        except Exception:
            continue
    progress.empty()

    # Sinyaller üret
    with st.spinner("Sinyaller + HA skorları hesaplanıyor..."):
        gunluk_sinyaller = {}
        for sembol, df in hisse_verileri.items():
            ha = hisse_ha[sembol]
            sinyaller = sapan_sinyal_uret(df, ha, sembol, ema_tolerans,
                                           zaman_stopu, atr_kat, rr_kat)
            for s in sinyaller:
                tarih = s["tarih"]
                if tarih < bas_ts or tarih > bit_ts:
                    continue
                if endeks_aktif and not endeks_f.get(tarih.date(), True):
                    continue
                # HA eşik filtresi (sadece "Eşik filtresi" modunda)
                if ha_mod.startswith("Eşik") and s["ha_skor"] < ha_esik:
                    continue
                gunluk_sinyaller.setdefault(tarih, []).append(s)

    # Pozisyon yönetimi — acilis backtest ile aynı mantık
    with st.spinner("Pozisyon yönetimi simüle ediliyor..."):
        portfoy_s    = portfoy
        acik_pozlar  = []
        kapali_islem = []
        atlanan      = 0

        tum_tarihler = sorted(set(
            d for df in hisse_verileri.values()
            for d in df.index
            if bas_ts <= d <= bit_ts
        ))

        for tarih in tum_tarihler:
            # Açık pozisyonları kontrol et
            kapalanlar = []
            for poz in acik_pozlar:
                sembol = poz["sembol"]
                if sembol not in hisse_verileri:
                    continue
                df     = hisse_verileri[sembol]
                gunluk = df[df.index == tarih]
                if gunluk.empty:
                    continue

                gun_low  = float(gunluk.iloc[0]["Low"])
                gun_high = float(gunluk.iloc[0]["High"])

                gun_sayisi  = (tarih - poz["acilis"]).days
                zaman_doldu = gun_sayisi >= poz["zaman_stopu_gun"]

                sonuc = None
                cikis = None
                if gun_low <= poz["stop"]:
                    sonuc = "stop"
                    cikis = poz["stop"]
                elif gun_high >= poz["hedef"]:
                    sonuc = "hedef"
                    cikis = poz["hedef"]
                elif zaman_doldu:
                    sonuc = "zaman"
                    cikis = float(gunluk.iloc[0]["Close"])

                if sonuc:
                    kaz = (cikis - poz["giris"]) * poz["lot"]
                    portfoy_s += kaz
                    sonuc_label = {
                        "hedef": "✅ Hedef",
                        "stop" : "❌ Stop",
                        "zaman": "⏱️ Zaman",
                    }[sonuc]
                    kapali_islem.append({
                        "Açılış"     : poz["acilis"].strftime("%d.%m.%Y"),
                        "Kapanış"    : tarih.strftime("%d.%m.%Y"),
                        "Gün"        : gun_sayisi,
                        "Hisse"      : sembol,
                        "★"          : "★" if poz["top50"] else "",
                        "HA Skor"    : poz["ha_skor"],
                        "HA Dilim"   : ha_dilim(poz["ha_skor"]),
                        "HA Detay"   : poz["ha_detay"],
                        "Lot"        : poz["lot"],
                        "Giriş"      : round(poz["giris"], 2),
                        "Alış (TL)"  : round(poz["giris"] * poz["lot"], 0),
                        "Stop"       : round(poz["stop"], 2),
                        "Hedef"      : round(poz["hedef"], 2),
                        "Çıkış"      : round(cikis, 2),
                        "Satış (TL)" : round(cikis * poz["lot"], 0),
                        "Sonuç"      : sonuc_label,
                        "K/Z (TL)"   : round(kaz, 0),
                        "Portföy"    : round(portfoy_s, 0),
                    })
                    kapalanlar.append(poz)

            for k in kapalanlar:
                acik_pozlar.remove(k)

            # Yeni sinyaller — TOP50 önce, sonra HA skoru yüksek olan önce
            if tarih in gunluk_sinyaller:
                sinyaller_bugun = sorted(
                    gunluk_sinyaller[tarih],
                    key=lambda x: (not x["top50"], -x["ha_skor"])
                )
                for sinyal in sinyaller_bugun:
                    if any(p["sembol"] == sinyal["sembol"] for p in acik_pozlar):
                        continue
                    if len(acik_pozlar) >= max_pozisyon:
                        atlanan += 1
                        continue
                    poz_tl = portfoy_s * (poz_yuzde / 100)
                    lot    = max(1, int(poz_tl / sinyal["giris"]))
                    acik_pozlar.append({
                        "sembol"        : sinyal["sembol"],
                        "acilis"        : tarih,
                        "giris"         : sinyal["giris"],
                        "stop"          : sinyal["stop"],
                        "hedef"         : sinyal["hedef"],
                        "lot"           : lot,
                        "top50"         : sinyal["top50"],
                        "zaman_stopu_gun": sinyal["zaman_stopu_gun"],
                        "ha_skor"       : sinyal["ha_skor"],
                        "ha_detay"      : sinyal["ha_detay"],
                    })

        # Açık kalan pozisyonları son fiyatla kapat
        for poz in acik_pozlar:
            sembol = poz["sembol"]
            if sembol not in hisse_verileri:
                continue
            df    = hisse_verileri[sembol]
            son   = df.iloc[-1]
            cikis = float(son["Close"])
            kaz   = (cikis - poz["giris"]) * poz["lot"]
            portfoy_s += kaz
            gun_sayisi = (son.name - poz["acilis"]).days
            kapali_islem.append({
                "Açılış"     : poz["acilis"].strftime("%d.%m.%Y"),
                "Kapanış"    : son.name.strftime("%d.%m.%Y"),
                "Gün"        : gun_sayisi,
                "Hisse"      : sembol,
                "★"          : "★" if poz["top50"] else "",
                "HA Skor"    : poz["ha_skor"],
                "HA Dilim"   : ha_dilim(poz["ha_skor"]),
                "HA Detay"   : poz["ha_detay"],
                "Lot"        : poz["lot"],
                "Giriş"      : round(poz["giris"], 2),
                "Alış (TL)"  : round(poz["giris"] * poz["lot"], 0),
                "Stop"       : round(poz["stop"], 2),
                "Hedef"      : round(poz["hedef"], 2),
                "Çıkış"      : round(cikis, 2),
                "Satış (TL)" : round(cikis * poz["lot"], 0),
                "Sonuç"      : "⏳ Açık",
                "K/Z (TL)"   : round(kaz, 0),
                "Portföy"    : round(portfoy_s, 0),
            })

    st.session_state["kapali"]    = kapali_islem
    st.session_state["portfoy_s"] = portfoy_s
    st.session_state["portfoy0"]  = portfoy
    st.session_state["atlanan"]   = atlanan
    st.session_state["ha_mod"]    = ha_mod

# ─── SONUÇLAR ─────────────────────────────────────────────────────────────────
if "kapali" in st.session_state:
    kapali    = st.session_state["kapali"]
    portfoy_s = st.session_state["portfoy_s"]
    portfoy0  = st.session_state["portfoy0"]
    atlanan   = st.session_state["atlanan"]
    ha_mod_s  = st.session_state.get("ha_mod", "")

    if not kapali:
        st.warning("Bu dönemde sinyal bulunamadı.")
        st.stop()

    df_i = pd.DataFrame(kapali)

    # Tamamlanan işlemler (açık olmayanlar)
    tamam = df_i[df_i["Sonuç"].isin(["✅ Hedef","❌ Stop","⏱️ Zaman"])].copy()
    kazanan  = tamam[tamam["Sonuç"] == "✅ Hedef"]
    kaybeden = tamam[tamam["Sonuç"] == "❌ Stop"]
    zamanli  = tamam[tamam["Sonuç"] == "⏱️ Zaman"]

    toplam     = len(tamam)
    net_kz     = df_i["K/Z (TL)"].sum()
    getiri_pct = (portfoy_s - portfoy0) / portfoy0 * 100
    win_rate   = len(kazanan) / toplam * 100 if toplam > 0 else 0

    brut_kar   = tamam[tamam["K/Z (TL)"] > 0]["K/Z (TL)"].sum()
    brut_zarar = abs(tamam[tamam["K/Z (TL)"] < 0]["K/Z (TL)"].sum())
    pf         = brut_kar / brut_zarar if brut_zarar > 0 else float("inf")

    ort_kaz = kazanan["K/Z (TL)"].mean() if len(kazanan) > 0 else 0
    ort_kay = kaybeden["K/Z (TL)"].mean() if len(kaybeden) > 0 else 0

    st.markdown(f"### 📊 Genel Sonuç — {ha_mod_s}")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, lbl, val, renk in [
        (c1, "Başlangıç",   f"{portfoy0:,.0f} TL",  "metric-neu"),
        (c2, "Bitiş",       f"{portfoy_s:,.0f} TL", "metric-pos" if portfoy_s >= portfoy0 else "metric-neg"),
        (c3, "Net K/Z",     f"{net_kz:+,.0f} TL",   "metric-pos" if net_kz >= 0 else "metric-neg"),
        (c4, "Getiri",      f"{getiri_pct:+.1f}%",  "metric-pos" if getiri_pct >= 0 else "metric-neg"),
        (c5, "Win Rate",    f"{win_rate:.1f}%",     "metric-pos" if win_rate >= 50 else "metric-neg"),
        (c6, "Profit Factor", f"{pf:.2f}" if pf != float('inf') else "∞", "metric-pos" if pf >= 1 else "metric-neg"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    c7, c8, c9, c10 = st.columns(4)
    for col, lbl, val, renk in [
        (c7,  "Toplam İşlem",     str(toplam),         "metric-neu"),
        (c8,  "Hedef (✅)",       str(len(kazanan)),   "metric-pos"),
        (c9,  "Stop (❌)",        str(len(kaybeden)),  "metric-neg"),
        (c10, "Zaman Stopu (⏱️)", str(len(zamanli)),   "metric-neu"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    if atlanan > 0:
        st.caption(f"ℹ️ {atlanan} sinyal pozisyon limiti dolu olduğu için atlandı.")

    st.markdown("---")

    # ─── HA SKOR DİLİM ANALİZİ ────────────────────────────────────────────────
    st.markdown("### 📡 HA Skor Dilimi Analizi")
    st.caption("Asıl soru: HA skoru yükseldikçe win rate / profit factor artıyor mu? "
               "Eğer 75-100 dilimi 0-25'ten belirgin iyiyse, HA skorlaması ayırt edici demektir.")

    dilim_satir = []
    for dilim in DILIM_SIRA:
        sub = tamam[tamam["HA Dilim"] == dilim]
        if len(sub) == 0:
            dilim_satir.append({
                "HA Dilim": dilim, "İşlem": 0, "Hedef": 0, "Stop": 0, "Zaman": 0,
                "Win Rate %": 0.0, "Profit Factor": 0.0,
                "Ort. K/Z (TL)": 0.0, "Toplam K/Z (TL)": 0.0,
            })
            continue
        s_kaz = sub[sub["Sonuç"] == "✅ Hedef"]
        s_kay = sub[sub["Sonuç"] == "❌ Stop"]
        s_zam = sub[sub["Sonuç"] == "⏱️ Zaman"]
        s_bk  = sub[sub["K/Z (TL)"] > 0]["K/Z (TL)"].sum()
        s_bz  = abs(sub[sub["K/Z (TL)"] < 0]["K/Z (TL)"].sum())
        s_pf  = s_bk / s_bz if s_bz > 0 else float("inf")
        dilim_satir.append({
            "HA Dilim"        : dilim,
            "İşlem"           : len(sub),
            "Hedef"           : len(s_kaz),
            "Stop"            : len(s_kay),
            "Zaman"           : len(s_zam),
            "Win Rate %"      : round(len(s_kaz) / len(sub) * 100, 1),
            "Profit Factor"   : round(s_pf, 2) if s_pf != float("inf") else 999.0,
            "Ort. K/Z (TL)"   : round(sub["K/Z (TL)"].mean(), 0),
            "Toplam K/Z (TL)" : round(sub["K/Z (TL)"].sum(), 0),
        })
    df_dilim = pd.DataFrame(dilim_satir)

    cda, cdb = st.columns([1, 1])
    with cda:
        st.dataframe(
            df_dilim.style.format({
                "Win Rate %": "{:.1f}",
                "Profit Factor": lambda x: "∞" if x >= 999 else f"{x:.2f}",
                "Ort. K/Z (TL)": "{:+,.0f}",
                "Toplam K/Z (TL)": "{:+,.0f}",
            }),
            use_container_width=True, hide_index=True
        )
    with cdb:
        fig_d = go.Figure()
        fig_d.add_trace(go.Bar(
            x=df_dilim["HA Dilim"], y=df_dilim["Win Rate %"],
            marker_color=["#ef4444","#f59e0b","#3b82f6","#22c55e"],
            text=[f"{v:.1f}%" for v in df_dilim["Win Rate %"]],
            textposition="outside", name="Win Rate %",
        ))
        fig_d.add_hline(y=win_rate, line_dash="dash", line_color="#94a3b8",
                        annotation_text=f"Genel: {win_rate:.1f}%")
        fig_d.update_layout(
            template="plotly_dark", paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
            height=300, margin=dict(l=10,r=10,t=20,b=10),
            yaxis=dict(gridcolor="#1e293b", ticksuffix="%"),
            xaxis=dict(gridcolor="#1e293b", title="HA Skor Dilimi"),
            showlegend=False,
        )
        st.plotly_chart(fig_d, use_container_width=True)

    # İşlem sayısı az olan dilimler için uyarı
    az_dilim = df_dilim[(df_dilim["İşlem"] > 0) & (df_dilim["İşlem"] < 10)]
    if len(az_dilim) > 0:
        st.warning(f"⚠️ Şu dilimlerde işlem sayısı 10'un altında, istatistik güvenilirliği düşük: "
                   f"{', '.join(az_dilim['HA Dilim'])}. Sonuçları temkinli yorumla.")

    # ─── HAM EŞİK KARŞILAŞTIRMASI (55) ────────────────────────────────────────
    st.markdown("### 🎯 HA 55 Eşiği — Var / Yok Karşılaştırması")
    st.caption("`ha_tarayici.py`'nin 'sinyal var' saydığı 55 eşiğine göre ikili kıyas. "
               "Bu mod 'Sadece etiketle' iken anlamlı — tüm sinyaller alınmış olur, "
               "HA sinyali olan ve olmayan grupların performansı karşılaştırılır.")

    esik_satir = []
    for ad, mask in [
        ("HA Sinyali VAR (skor ≥ 55)", tamam["HA Skor"] >= 55),
        ("HA Sinyali YOK (skor < 55)", tamam["HA Skor"] < 55),
    ]:
        sub = tamam[mask]
        if len(sub) == 0:
            esik_satir.append({
                "Grup": ad, "İşlem": 0, "Win Rate %": 0.0,
                "Profit Factor": 0.0, "Ort. K/Z (TL)": 0.0, "Toplam K/Z (TL)": 0.0,
            })
            continue
        s_kaz = sub[sub["Sonuç"] == "✅ Hedef"]
        s_bk  = sub[sub["K/Z (TL)"] > 0]["K/Z (TL)"].sum()
        s_bz  = abs(sub[sub["K/Z (TL)"] < 0]["K/Z (TL)"].sum())
        s_pf  = s_bk / s_bz if s_bz > 0 else float("inf")
        esik_satir.append({
            "Grup"            : ad,
            "İşlem"           : len(sub),
            "Win Rate %"      : round(len(s_kaz) / len(sub) * 100, 1),
            "Profit Factor"   : round(s_pf, 2) if s_pf != float("inf") else 999.0,
            "Ort. K/Z (TL)"   : round(sub["K/Z (TL)"].mean(), 0),
            "Toplam K/Z (TL)" : round(sub["K/Z (TL)"].sum(), 0),
        })
    df_esik = pd.DataFrame(esik_satir)
    st.dataframe(
        df_esik.style.format({
            "Win Rate %": "{:.1f}",
            "Profit Factor": lambda x: "∞" if x >= 999 else f"{x:.2f}",
            "Ort. K/Z (TL)": "{:+,.0f}",
            "Toplam K/Z (TL)": "{:+,.0f}",
        }),
        use_container_width=True, hide_index=True
    )

    st.markdown("---")

    # ─── SEKMELER ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["💰 Portföy Eğrisi", "📆 Yıllık Performans", "📋 İşlem Listesi"])

    with tab1:
        df_i["Kapanış_dt"] = pd.to_datetime(df_i["Kapanış"], format="%d.%m.%Y")
        df_sorted = df_i.sort_values("Kapanış_dt")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_sorted["Kapanış_dt"], y=df_sorted["Portföy"],
            fill="tozeroy", line=dict(color="#38bdf8", width=2),
            fillcolor="rgba(56,189,248,0.08)", name="Portföy"
        ))
        fig.add_hline(y=portfoy0, line_dash="dash", line_color="#64748b",
                      line_width=1, annotation_text=f"Başlangıç: {portfoy0:,.0f} TL")
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
            height=400, margin=dict(l=10,r=10,t=20,b=10),
            yaxis=dict(gridcolor="#1e293b", tickformat=",.0f", ticksuffix=" TL"),
            xaxis=dict(gridcolor="#1e293b"), showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_i["Yil"] = df_i["Kapanış_dt"].dt.year
        yillik_list = []
        portfoy_bas = portfoy0
        for yil in sorted(df_i["Yil"].unique()):
            sub = df_i[df_i["Yil"] == yil]
            kz  = sub["K/Z (TL)"].sum()
            portfoy_son = portfoy_bas + kz
            getiri_yil  = kz / portfoy_bas * 100
            tamam_yil   = sub[sub["Sonuç"].isin(["✅ Hedef","❌ Stop","⏱️ Zaman"])]
            kaz_yil     = (sub["Sonuç"] == "✅ Hedef").sum()
            kay_yil     = (sub["Sonuç"] == "❌ Stop").sum()
            wr_yil      = kaz_yil / len(tamam_yil) * 100 if len(tamam_yil) > 0 else 0
            yillik_list.append({
                "Yıl"          : yil,
                "Başlangıç TL" : round(portfoy_bas, 0),
                "Bitiş TL"     : round(portfoy_son, 0),
                "K/Z (TL)"     : round(kz, 0),
                "Getiri %"     : round(getiri_yil, 1),
                "Win Rate %"   : round(wr_yil, 1),
                "Toplam İşlem" : len(tamam_yil),
                "Kazanan"      : int(kaz_yil),
                "Kaybeden"     : int(kay_yil),
            })
            portfoy_bas = portfoy_son
        df_yil = pd.DataFrame(yillik_list)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=df_yil["Yıl"].astype(str), y=df_yil["Getiri %"],
            marker_color=[("#3fb950" if v >= 0 else "#ef4444") for v in df_yil["Getiri %"]],
            text=[f"{v:+.1f}%" for v in df_yil["Getiri %"]], textposition="outside",
        ))
        fig3.add_hline(y=0, line_dash="dot", line_color="#64748b", line_width=1)
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
            height=320, margin=dict(l=10,r=10,t=30,b=10),
            yaxis=dict(gridcolor="#1e293b", ticksuffix="%"),
            xaxis=dict(gridcolor="#1e293b"), showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)
        df_yil_g = df_yil.copy()
        for cc in ["Başlangıç TL","Bitiş TL"]:
            df_yil_g[cc] = df_yil_g[cc].apply(lambda x: f"{x:,.0f}")
        df_yil_g["K/Z (TL)"]   = df_yil_g["K/Z (TL)"].apply(lambda x: f"{x:+,.0f}")
        df_yil_g["Getiri %"]   = df_yil_g["Getiri %"].apply(lambda x: f"{x:+.1f}%")
        df_yil_g["Win Rate %"] = df_yil_g["Win Rate %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_yil_g, use_container_width=True, hide_index=True)

    with tab3:
        df_g = df_i.drop(columns=["Kapanış_dt","Yil"], errors="ignore").copy()
        for cc in ["Alış (TL)","Satış (TL)","Portföy"]:
            df_g[cc] = df_g[cc].apply(lambda x: f"{x:,.0f}")
        df_g["K/Z (TL)"] = df_g["K/Z (TL)"].apply(lambda x: f"{x:+,.0f}")
        st.dataframe(
            df_g[[
                "Açılış","Kapanış","Gün","Hisse","★","HA Skor","HA Dilim","HA Detay",
                "Lot","Giriş","Alış (TL)","Stop","Hedef","Çıkış","Satış (TL)",
                "Sonuç","K/Z (TL)","Portföy"
            ]],
            use_container_width=True, hide_index=True
        )
        csv = df_i.drop(columns=["Kapanış_dt","Yil"], errors="ignore").to_csv(
            index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSV İndir", data=csv,
            file_name=f"sapan_ha_backtest_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir. HA skoru `ha_tarayici.py` mantığıyla, "
               "Sapan sinyali `bist_sapan_telegram_bot.py` ile birebir hesaplanır.")
