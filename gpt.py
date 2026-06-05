bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/bist_sapan_backtest_acilis_mae.py')
s=p.read_text()
# Insert update of extremes after gun_low/high
s=s.replace('''                gun_low  = float(gunluk.iloc[0]["Low"])
                gun_high = float(gunluk.iloc[0]["High"])

                # Zaman stopu kontrolü''','''                gun_low  = float(gunluk.iloc[0]["Low"])
                gun_high = float(gunluk.iloc[0]["High"])

                # MAE/MFE takibi: pozisyon açıkken görülen en düşük/yüksek fiyat
                poz["en_dusuk"] = min(float(poz.get("en_dusuk", poz["giris"])), gun_low)
                poz["en_yuksek"] = max(float(poz.get("en_yuksek", poz["giris"])), gun_high)

                # Zaman stopu kontrolü''')
# Insert MAE calculations before append
s=s.replace('''                    sonuc_label = {
                        "hedef": "✅ Hedef",
                        "stop" : "❌ Stop",
                        "zaman": "⏱️ Zaman",
                    }[sonuc]
                    kapali_islem.append({''','''                    sonuc_label = {
                        "hedef": "✅ Hedef",
                        "stop" : "❌ Stop",
                        "zaman": "⏱️ Zaman",
                    }[sonuc]

                    bir_r = max(float(poz.get("bir_r", poz["giris"] - poz["stop"])), 1e-10)
                    en_dusuk = float(poz.get("en_dusuk", poz["giris"]))
                    en_yuksek = float(poz.get("en_yuksek", poz["giris"]))
                    mae_tl = max(0.0, poz["giris"] - en_dusuk)
                    mfe_tl = max(0.0, en_yuksek - poz["giris"])
                    mae_pct = mae_tl / poz["giris"] * 100
                    mfe_pct = mfe_tl / poz["giris"] * 100
                    mae_r = mae_tl / bir_r
                    mfe_r = mfe_tl / bir_r

                    kapali_islem.append({''')
# add fields after Portföy in closed append
s=s.replace('''                        "K/Z (TL)"   : round(kaz, 0),
                        "Portföy"    : round(portfoy_s, 0),
                    })''','''                        "K/Z (TL)"   : round(kaz, 0),
                        "Portföy"    : round(portfoy_s, 0),
                        "Bir R"      : round(bir_r, 2),
                        "En Düşük"   : round(en_dusuk, 2),
                        "En Yüksek"  : round(en_yuksek, 2),
                        "MAE %"      : round(mae_pct, 2),
                        "MAE R"      : round(mae_r, 2),
                        "MFE %"      : round(mfe_pct, 2),
                        "MFE R"      : round(mfe_r, 2),
                    })''',1)
# add fields to new position
s=s.replace('''                        "hedef"         : sinyal["hedef"],
                        "lot"           : lot,''','''                        "hedef"         : sinyal["hedef"],
                        "bir_r"         : sinyal["bir_r"],
                        "en_dusuk"      : sinyal["giris"],
                        "en_yuksek"     : sinyal["giris"],
                        "lot"           : lot,''')
# open positions calculations before append
s=s.replace('''            cikis = float(son["Close"])
            kaz   = (cikis - poz["giris"]) * poz["lot"]
            portfoy_s += kaz
            gun_sayisi = (son.name - poz["acilis"]).days
            kapali_islem.append({''','''            cikis = float(son["Close"])
            kaz   = (cikis - poz["giris"]) * poz["lot"]
            portfoy_s += kaz
            gun_sayisi = (son.name - poz["acilis"]).days

            # Açık kalan işlem için de o ana kadarki MAE/MFE hesaplanır
            bir_r = max(float(poz.get("bir_r", poz["giris"] - poz["stop"])), 1e-10)
            sub_df = df[(df.index >= poz["acilis"]) & (df.index <= son.name)]
            en_dusuk = float(sub_df["Low"].min()) if not sub_df.empty else float(poz.get("en_dusuk", poz["giris"]))
            en_yuksek = float(sub_df["High"].max()) if not sub_df.empty else float(poz.get("en_yuksek", poz["giris"]))
            mae_tl = max(0.0, poz["giris"] - en_dusuk)
            mfe_tl = max(0.0, en_yuksek - poz["giris"])
            mae_pct = mae_tl / poz["giris"] * 100
            mfe_pct = mfe_tl / poz["giris"] * 100
            mae_r = mae_tl / bir_r
            mfe_r = mfe_tl / bir_r

            kapali_islem.append({''')
# add fields to open append after Portföy occurrence second? Need replace remaining original for open block
s=s.replace('''                "K/Z (TL)"   : round(kaz, 0),
                "Portföy"    : round(portfoy_s, 0),
            })''','''                "K/Z (TL)"   : round(kaz, 0),
                "Portföy"    : round(portfoy_s, 0),
                "Bir R"      : round(bir_r, 2),
                "En Düşük"   : round(en_dusuk, 2),
                "En Yüksek"  : round(en_yuksek, 2),
                "MAE %"      : round(mae_pct, 2),
                "MAE R"      : round(mae_r, 2),
                "MFE %"      : round(mfe_pct, 2),
                "MFE R"      : round(mfe_r, 2),
            })''')
# Insert MAE summary after ort_kay
marker='''    ort_kaz = df_i[df_i["Sonuç"]=="✅ Hedef"]["K/Z (TL)"].mean() if len(kazanan) > 0 else 0
    ort_kay = df_i[df_i["Sonuç"]=="❌ Stop"]["K/Z (TL)"].mean()  if len(kaybeden) > 0 else 0

    # Metrik kartları'''
repl='''    ort_kaz = df_i[df_i["Sonuç"]=="✅ Hedef"]["K/Z (TL)"].mean() if len(kazanan) > 0 else 0
    ort_kay = df_i[df_i["Sonuç"]=="❌ Stop"]["K/Z (TL)"].mean()  if len(kaybeden) > 0 else 0

    # MAE/MFE özeti — özellikle hedefe ulaşan işlemler
    tp_mae = kazanan["MAE R"].dropna() if "MAE R" in kazanan.columns else pd.Series(dtype=float)
    tp_mfe = kazanan["MFE R"].dropna() if "MFE R" in kazanan.columns else pd.Series(dtype=float)
    mae_ort = tp_mae.mean() if len(tp_mae) else 0
    mae_med = tp_mae.median() if len(tp_mae) else 0
    mae_p75 = tp_mae.quantile(0.75) if len(tp_mae) else 0
    mae_p90 = tp_mae.quantile(0.90) if len(tp_mae) else 0
    mfe_ort = tp_mfe.mean() if len(tp_mfe) else 0

    # Metrik kartları'''
s=s.replace(marker,repl)
# add extra metric cards after c11 c12 block maybe before st.markdown("---")
marker2='''    st.markdown("---")

    # Sekmeler
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Portföy Eğrisi", "📅 Aylık Performans", "📆 Yıllık Performans", "📋 İşlem Listesi"])'''
repl2='''    st.markdown("")

    c13, c14, c15, c16, c17 = st.columns(5)
    for col, lbl, val, renk in [
        (c13, "TP Ort. MAE", f"{mae_ort:.2f}R", "metric-neu"),
        (c14, "TP Medyan MAE", f"{mae_med:.2f}R", "metric-neu"),
        (c15, "TP %75 MAE", f"{mae_p75:.2f}R", "metric-neu"),
        (c16, "TP %90 MAE", f"{mae_p90:.2f}R", "metric-neu"),
        (c17, "TP Ort. MFE", f"{mfe_ort:.2f}R", "metric-pos"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Sekmeler
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Portföy Eğrisi", "📅 Aylık Performans", "📆 Yıllık Performans", "📋 İşlem Listesi", "📉 MAE Analizi"])'''
s=s.replace(marker2,repl2)
# add tab5 before final markdown. Insert before st.markdown("---") at end? Need find after tab4 block ends.
insert='''
    with tab5:
        st.subheader("Hedefe Ulaşan İşlemlerde Maksimum Geri Çekilme (MAE)")
        st.caption("MAE R = İşlem hedefe/zamana/stopa gitmeden önce girişe karşı oluşan maksimum ters hareket / ilk risk.")

        if len(kazanan) == 0 or "MAE R" not in kazanan.columns:
            st.warning("MAE analizi için hedefe ulaşan işlem bulunamadı.")
        else:
            dagilim = []
            for esik in [0.25, 0.50, 0.75, 1.00, 1.25, 1.50]:
                oran = (tp_mae <= esik).mean() * 100 if len(tp_mae) else 0
                adet = int((tp_mae <= esik).sum()) if len(tp_mae) else 0
                dagilim.append({
                    "Eşik": f"≤ {esik:.2f}R",
                    "İşlem Adedi": adet,
                    "TP İşlemleri İçindeki Oran": f"%{oran:.1f}",
                })

            ozet = pd.DataFrame([
                {"Metrik": "TP işlem sayısı", "Değer": len(kazanan)},
                {"Metrik": "Ortalama MAE R", "Değer": round(mae_ort, 2)},
                {"Metrik": "Medyan MAE R", "Değer": round(mae_med, 2)},
                {"Metrik": "%75 persentil MAE R", "Değer": round(mae_p75, 2)},
                {"Metrik": "%90 persentil MAE R", "Değer": round(mae_p90, 2)},
                {"Metrik": "Ortalama MFE R", "Değer": round(mfe_ort, 2)},
            ])

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### Özet")
                st.dataframe(ozet, use_container_width=True, hide_index=True)
            with col_b:
                st.markdown("#### MAE Eşik Dağılımı")
                st.dataframe(pd.DataFrame(dagilim), use_container_width=True, hide_index=True)

            fig_mae = go.Figure()
            fig_mae.add_trace(go.Histogram(x=tp_mae, nbinsx=30, name="TP MAE R"))
            fig_mae.add_vline(x=mae_med, line_dash="dash", line_color="#facc15", annotation_text="Medyan")
            fig_mae.add_vline(x=mae_p75, line_dash="dot", line_color="#38bdf8", annotation_text="%75")
            fig_mae.update_layout(
                template="plotly_dark", paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
                height=350, margin=dict(l=10,r=10,t=30,b=10),
                xaxis_title="MAE R", yaxis_title="İşlem Sayısı",
                yaxis=dict(gridcolor="#1e293b"), xaxis=dict(gridcolor="#1e293b"),
                showlegend=False,
            )
            st.plotly_chart(fig_mae, use_container_width=True)

            st.markdown("#### TP İşlem Detayı")
            detay_kolonlar = [
                "Açılış", "Kapanış", "Gün", "Hisse", "Giriş", "Stop", "Hedef",
                "En Düşük", "En Yüksek", "MAE %", "MAE R", "MFE %", "MFE R", "K/Z (TL)"
            ]
            st.dataframe(kazanan[detay_kolonlar].sort_values("MAE R"), use_container_width=True, hide_index=True)

'''
# place before final separator caption near end
s=s.replace('''    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")''', insert + '''    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")''')
# update display table include columns
s=s.replace('''                "Çıkış","Satış (TL)","Sonuç","K/Z (TL)","Portföy"
            ]],''','''                "Çıkış","Satış (TL)","Sonuç","K/Z (TL)","Portföy",
                "Bir R","En Düşük","En Yüksek","MAE %","MAE R","MFE %","MFE R"
            ]],''')
p.write_text(s)
PY
python -m py_compile /mnt/data/bist_sapan_backtest_acilis_mae.py
ls -l /mnt/data/bist_sapan_backtest_acilis_mae.py
