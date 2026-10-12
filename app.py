"""
Logo ERP Çift Yönlü Sesli Denetim Asistanı
-------------------------------------------
Bu modül; doğal dil işleme, kural tabanlı regex filtreleme ve çift yönlü ses teknolojilerini 
kullanarak Logo ERP fatura verilerini denetleyen kurumsal bir Streamlit arayüzü sunar.
"""

import asyncio
import io
import re
from datetime import datetime
import pandas as pd
import requests
import speech_recognition as sr
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import edge_tts

# ---------------------------------------------------------
# Sayfa Konfigürasyonu
# ---------------------------------------------------------
st.set_page_config(
    page_title="Logo ERP Sesli Asistan",
    page_icon="🎙️",
    layout="centered"
)

# ---------------------------------------------------------
# 1. Ses Motoru Katmanı (Microsoft Edge TTS)
# ---------------------------------------------------------
async def _ses_uret_async(metin: str) -> bytes:
    """Metni tok ve kurumsal bir Türkçe erkek sesi (tr-TR-AhmetNeural) ile ses dosyasına dönüştürür."""
    communicate = edge_tts.Communicate(metin, voice="tr-TR-AhmetNeural")
    ses_akisi = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            ses_akisi.extend(chunk["data"])
    return bytes(ses_akisi)

def sesli_cevap_ver(metin: str):
    """Üretilen ses baytlarını Streamlit bileşeni olarak otomatik oynatır."""
    ses_bayt = asyncio.run(_ses_uret_async(metin))
    st.audio(ses_bayt, format="audio/mp3", autoplay=True)

# ---------------------------------------------------------
# 2. Veri Yönetimi ve Sütun Eşleştirme Katmanı
# ---------------------------------------------------------
@st.cache_data
def veriyi_yukle() -> pd.DataFrame:
    """
    Excel fatura verisini içe aktarır, farklı ERP başlıklarını 
    standart veri modeline normalize eder.
    """
    df = pd.read_excel("logo_faturalar.xlsx")
    kolon_haritasi = {
        "FATURA NO": "Fatura_No", "BELGE_NO": "Fatura_No", "Fatura No": "Fatura_No",
        "CARİ": "Cari_Unvan", "CARİ ADI": "Cari_Unvan", "UNVAN": "Cari_Unvan", "Cari Ünvan": "Cari_Unvan",
        "TUTAR": "Tutar", "TOPLAM": "Tutar", "NET TUTAR": "Tutar",
        "DURUM": "Durum", "STATÜ": "Durum",
        "HATA": "Hata_Aciklamasi", "HATA AÇIKLAMASI": "Hata_Aciklamasi", "Hata Açıklaması": "Hata_Aciklamasi",
        "TARİH": "Tarih", "Tarih": "Tarih"
    }
    df = df.rename(columns={k: v for k, v in kolon_haritasi.items() if k in df.columns})
    df["Tarih"] = df["Tarih"].astype(str)
    return df

# ---------------------------------------------------------
# 3. Canlı Entegrasyon Katmanı (Open-Meteo API)
# ---------------------------------------------------------
@st.cache_data(ttl=1800)
def hava_durumu_al() -> str:
    """
    Open-Meteo API üzerinden anlık saha hava durumunu ve sıcaklığı çeker.
    Bağlantı kesintilerinde fail-safe mantığı ile yedek değer basar.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=39.92&longitude=32.85&current=temperature_2m,weather_code"
        res = requests.get(url, timeout=3).json()
        sicaklik = round(res["current"]["temperature_2m"])
        kod = res["current"]["weather_code"]
        
        if kod == 0:
            durum, ikon = "Açık", "☀️"
        elif kod in [1, 2, 3]:
            durum, ikon = "Parçalı Bulutlu", "⛅"
        elif kod in [45, 48]:
            durum, ikon = "Sisli", "🌫️"
        elif kod in [51, 53, 55, 61, 63, 65]:
            durum, ikon = "Yağmurlu", "🌧️"
        else:
            durum, ikon = "Bulutlu", "☁️"
            
        return f"{ikon} <strong>Operasyon Sahası:</strong> {sicaklik}°C {durum}"
    except Exception:
        saat = datetime.now().hour
        tahmini_derece = 14 if (saat >= 18 or saat <= 7) else 21
        return f"☁️ <strong>Operasyon Sahası:</strong> {tahmini_derece}°C Bulutlu"

df = veriyi_yukle()

# ---------------------------------------------------------
# 4. Dinamik Sistem Durumu ve Başlık
# ---------------------------------------------------------
st.title("🎙️ Logo ERP Sesli Asistanı")
st.caption("Doğal Dil ve Kural Tabanlı Fatura Denetim Paneli")

gunler_tr = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
    "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
}
aylar_tr = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

simdi = datetime.now()
formatli_tarih = f"{simdi.day} {aylar_tr[simdi.month]} {simdi.year} {gunler_tr[simdi.strftime('%A')]}"
hava_bilgisi = hava_durumu_al()

st.markdown(
    f"""
    <div style="background-color:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; font-size:13px; color:#475569;">
        <span>📅 <strong>Sistem Tarihi:</strong> {formatli_tarih}</span>
        <span>{hava_bilgisi}</span>
        <span style="background-color:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:10px; font-weight:600;">ERP Çevrimiçi</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 5. Ses ve Metin Giriş Katmanı
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 10px; margin-bottom: 5px; font-weight: 500; font-size: 14px; color: #475569;'>🔍 Sesli Komut veya Metin ile Arama</div>", unsafe_allow_html=True)

col_mic, col_txt = st.columns([1, 6], vertical_alignment="center")

with col_mic:
    ses_verisi = audio_recorder(
        text="",
        recording_color="#ef4444",
        neutral_color="#3b82f6",
        icon_size="2x"
    )

aranan_kelime = ""

if ses_verisi:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(ses_verisi)) as source:
            audio_content = recognizer.record(source)
            aranan_kelime = recognizer.recognize_google(audio_content, language="tr-TR")
            st.success(f"Algılanan Komut: **{aranan_kelime}**")
    except sr.UnknownValueError:
        st.warning("Ses net anlaşılamadı, lütfen tekrar deneyin.")
    except Exception as e:
        st.error(f"Ses işlenirken hata oluştu: {e}")

with col_txt:
    metin_arama = st.text_input(
        label="Arama",
        value=aranan_kelime,
        placeholder="Örn: 'Sorunlu faturalar', '50000 üzeri', '10.09.2026'...",
        label_visibility="collapsed"
    )

aktif_arama = metin_arama if metin_arama else aranan_kelime

# ---------------------------------------------------------
# 6. Gelişmiş Filtreleme ve NLP Katmanı
# ---------------------------------------------------------
filtrelenmis_df = df.copy()

if aktif_arama:
    kelime = aktif_arama.lower().strip()
    
    aylar = {
        "ocak": "01", "şubat": "02", "mart": "03", "nisan": "04",
        "mayıs": "05", "haziran": "06", "temmuz": "07", "ağustos": "08",
        "eylül": "09", "ekim": "10", "kasım": "11", "aralık": "12"
    }
    
    tarih_bulundu = False
    
    # Metinsel Ay Eşleştirme ("10 eylül")
    for ay_adi, ay_kodu in aylar.items():
        eslesme = re.search(rf"(\d{{1,2}})\s+{ay_adi}", kelime)
        if eslesme:
            gun = eslesme.group(1).zfill(2)
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Tarih"].str.contains(f"-{ay_kodu}-{gun}")]
            tarih_bulundu = True
            break
            
    # Sayısal Tarih Formatları (GG.AA.YYYY / YYYY-AA-GG / GG.AA)
    if not tarih_bulundu:
        eslesme_dmy = re.search(r"(\d{1,2})[\./-](\d{1,2})[\./-](\d{4})", kelime)
        eslesme_ymd = re.search(r"(\d{4})[\./-](\d{1,2})[\./-](\d{1,2})", kelime)
        eslesme_dm = re.search(r"(\d{1,2})[\./-](\d{1,2})", kelime)
        
        if eslesme_dmy:
            gun, ay, yil = eslesme_dmy.group(1).zfill(2), eslesme_dmy.group(2).zfill(2), eslesme_dmy.group(3)
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Tarih"].str.contains(f"{yil}-{ay}-{gun}")]
            tarih_bulundu = True
        elif eslesme_ymd:
            yil, ay, gun = eslesme_ymd.group(1), eslesme_ymd.group(2).zfill(2), eslesme_ymd.group(3).zfill(2)
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Tarih"].str.contains(f"{yil}-{ay}-{gun}")]
            tarih_bulundu = True
        elif eslesme_dm:
            gun, ay = eslesme_dm.group(1).zfill(2), eslesme_dm.group(2).zfill(2)
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Tarih"].str.contains(f"-{ay}-{gun}")]
            tarih_bulundu = True

    # Kural Tabanlı Eşanlamlı ve Finansal Eşik Analizi
    if not tarih_bulundu:
        hatali_terimler = ["hata", "hatalı", "sorun", "problem", "uyarı", "geçersiz"]
        onay_terimleri = ["onay", "onaylı", "onaylanan", "başarılı", "geçerli", "tamam"]
        bekleme_terimleri = ["bekle", "bekleyen", "beklemede", "sıradaki"]
        
        sayi_eslesmesi = re.search(r"(\d+[\.,]?\d*)", kelime.replace(".", ""))
        
        if any(terim in kelime for terim in ["üzeri", "büyük", "fazla", "yüksek"]) and sayi_eslesmesi:
            esik_deger = float(sayi_eslesmesi.group(1))
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Tutar"] >= esik_deger]
        elif any(terim in kelime for terim in ["altı", "küçük", "az", "düşük"]) and sayi_eslesmesi:
            esik_deger = float(sayi_eslesmesi.group(1))
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Tutar"] <= esik_deger]
        elif any(terim in kelime for terim in hatali_terimler):
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Durum"] == "Hatalı"]
        elif any(terim in kelime for terim in onay_terimleri):
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Durum"] == "Onaylandı"]
        elif any(terim in kelime for terim in bekleme_terimleri):
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Durum"] == "Beklemede"]
        else:
            filtrelenmis_df = filtrelenmis_df[
                filtrelenmis_df["Cari_Unvan"].str.lower().str.contains(kelime) |
                filtrelenmis_df["Fatura_No"].str.lower().str.contains(kelime) |
                filtrelenmis_df["Hata_Aciklamasi"].astype(str).str.lower().str.contains(kelime)
            ]

# ---------------------------------------------------------
# 7. Yönetici KPI Gösterge Paneli
# ---------------------------------------------------------
toplam_sonuc = len(filtrelenmis_df)
hatali_sayisi = len(filtrelenmis_df[filtrelenmis_df["Durum"] == "Hatalı"])
toplam_tutar = filtrelenmis_df["Tutar"].sum() if toplam_sonuc > 0 else 0.0
hata_orani = (hatali_sayisi / toplam_sonuc * 100) if toplam_sonuc > 0 else 0.0

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("İncelenen Fatura", f"{toplam_sonuc} Adet")
kpi2.metric("Toplam Hacim", f"{toplam_tutar:,.0f} TL".replace(",", "."))
kpi3.metric("Hatalı Kayıt", f"{hatali_sayisi} Adet", delta=f"-{hatali_sayisi}" if hatali_sayisi > 0 else None, delta_color="inverse")
kpi4.metric("Hata Oranı", f"%{hata_orani:.1f}")

# ---------------------------------------------------------
# 8. Çift Yönlü Sesli Raporlama
# ---------------------------------------------------------
if aktif_arama:
    if toplam_sonuc == 0:
        cevap = f"{aktif_arama} kriterine uygun fatura kaydı bulunamadı."
    elif hatali_sayisi > 0:
        cevap = f"{toplam_sonuc} adet fatura bulundu. Bunların {hatali_sayisi} tanesi denetim sırasında hatalı olarak işaretlendi."
    else:
        cevap = f"{toplam_sonuc} adet fatura listelendi. Tüm kayıtlar onaylı durumda."
    
    sesli_cevap_ver(cevap)

st.divider()

# ---------------------------------------------------------
# 9. Dinamik Fatura Kartları & Durum Tasarımı
# ---------------------------------------------------------
if toplam_sonuc == 0:
    st.markdown(
        f"""
        <div style="
            background-color: #f8fafc;
            border: 1px dashed #cbd5e1;
            border-radius: 10px;
            padding: 24px;
            text-align: center;
            color: #64748b;
            margin-top: 15px;
        ">
            <span style="font-size: 28px;">🔍</span>
            <div style="font-size: 15px; font-weight: 600; color: #334155; margin-top: 8px;">Sonuç Bulunamadı</div>
            <div style="font-size: 13px; margin-top: 4px;">"{aktif_arama}" aramasına uygun bir fatura kaydı eşleşmedi. Farklı bir cari adı, tutar veya durum deneyebilirsiniz.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    for _, row in filtrelenmis_df.iterrows():
        if row["Durum"] == "Hatalı":
            border_color = "#ef4444"
            badge_bg = "#fee2e2"
            badge_color = "#991b1b"
            icon = "⚠️"
        elif row["Durum"] == "Onaylandı":
            border_color = "#22c55e"
            badge_bg = "#dcfce7"
            badge_color = "#166534"
            icon = "✅"
        else:
            border_color = "#eab308"
            badge_bg = "#fef9c3"
            badge_color = "#854d0e"
            icon = "⏳"

        hata_kutusu = (
            f"""
            <div style="
                margin-top: 10px;
                font-size: 13px;
                color: #991b1b;
                background-color: #fef2f2;
                border-left: 3px solid #ef4444;
                padding: 8px 12px;
                border-radius: 4px;
            ">
                <strong>Hata Tespiti:</strong> {row['Hata_Aciklamasi']}
            </div>
            """
            if row["Durum"] == "Hatalı" else ""
        )

        st.markdown(
            f"""
            <div style="
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-left: 6px solid {border_color};
                border-radius: 10px;
                padding: 16px 18px;
                margin-bottom: 14px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; margin-bottom: 10px;">
                    <div>
                        <span style="font-size: 16px; font-weight: 700; color: #0f172a; letter-spacing: 0.3px;">{row['Fatura_No']}</span>
                        <span style="font-size: 12px; color: #64748b; margin-left: 8px;">📅 {row['Tarih']}</span>
                    </div>
                    <span style="background-color: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 16px; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">
                        {icon} {row['Durum']}
                    </span>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #1e293b;">
                    {row['Cari_Unvan']}
                </div>
                <div style="margin-top: 6px; font-size: 14px; color: #475569; display: flex; justify-content: space-between; align-items: baseline;">
                    <span>Fatura Tutarı:</span>
                    <span style="font-size: 18px; font-weight: 700; color: #0f172a;">{row['Tutar']:,.2f} TL</span>
                </div>
                {hata_kutusu}
            </div>
            """,
            unsafe_allow_html=True
        )