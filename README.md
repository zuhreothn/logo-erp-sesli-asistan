# 🎙️ Logo ERP Çift Yönlü Sesli Denetim Asistanı

Doğal dil işleme (NLP), kural tabanlı regex filtreleme ve çift yönlü ses teknolojilerini bir araya getiren kurumsal fatura denetim paneli prototipidir.

## Temel Özellikler
- **Çift Yönlü Sesli Etkileşim:** `SpeechRecognition` ile Türkçe sesli komut algılama; `edge-tts` (`tr-TR-AhmetNeural`) ile tok ve kurumsal erkek sesiyle anlık sesli raporlama.
- **Kural Tabanlı NLP & Regex Filtreleme:**
  - *Tarih Ayrıştırma:* `GG.AA.YYYY`, `YYYY-AA-GG` ve sözel ay formatları (`"12 Eylül"`).
  - *Sayısal Eşik Analizi:* Tutar bazlı sorgular (`"50000 üzeri"`, `"30000 altı"`).
  - *Eşanlamlı Durum Denetimi:* Fatura statüleri (`"sorunlu"`, `"hatalı"`, `"onaylanan"`).
- **Esnek Sütun Eşleştirici (Column Mapping):** Farklı ERP başlıklarını (`BELGE NO`, `CARİ ADI`) standart şemaya normalize eden katman.
- **Dinamik Sistem Durumu:** Otomatik güncellenen Türkçe sistem tarihi ve Open-Meteo API entegrasyonlu canlı hava durumu/operasyon sahası kartı.
- **Yönetici KPI Paneli & Dinamik Arayüz:** İncelenen fatura adedi, toplam finansal işlem hacmi (TL) ve yüzde bazlı hata oranını anlık hesaplayan kart mimarisi.

## Kurulum & Çalıştırma
```bash
# Gerekli bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
streamlit run app.py