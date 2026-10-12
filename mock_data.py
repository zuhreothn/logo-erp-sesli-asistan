import pandas as pd

# Logo ERP E-Fatura simülasyon verisi
data = [
    { 
        "Fatura_No": "GIB2026000000101",
        "Cari_Unvan": "Atlas Lojistik Hizmetleri A.Ş.",
        "Tarih": "2026-09-10",
        "Tutar": 48500.00,
        "Durum": "Hatalı",
        "Hata_Kodu": "ERR_VKN_01",
        "Hata_Aciklamasi": "Alıcı Vergi Kimlik Numarası (VKN) GİB sisteminde geçersiz."
    },
    {
        "Fatura_No": "GIB2026000000102",
        "Cari_Unvan": "Mavi Bilişim ve Yazılım Ltd. Şti.",
        "Tarih": "2026-09-11",
        "Tutar": 14200.50,
        "Durum": "Onaylandı",
        "Hata_Kodu": "-",
        "Hata_Aciklamasi": "GİB posta kutusuna başarıyla iletildi."
    },
    {
        "Fatura_No": "GIB2026000000103",
        "Cari_Unvan": "Özkan Ağır Sanayi A.Ş.",
        "Tarih": "2026-09-11",
        "Tutar": 125000.00,
        "Durum": "Hatalı",
        "Hata_Kodu": "ERR_TAX_404",
        "Hata_Aciklamasi": "KDV Tevkifat kodu girilmemiş veya oran uyuşmuyor."
    },
    {
        "Fatura_No": "GIB2026000000104",
        "Cari_Unvan": "Zirve Perakende ve Gıda San. Tic.",
        "Tarih": "2026-09-12",
        "Tutar": 6800.00,
        "Durum": "Beklemede",
        "Hata_Kodu": "-",
        "Hata_Aciklamasi": "İmza sürecinde, GİB kuyruğuna alınmayı bekliyor."
    },
    {
        "Fatura_No": "GIB2026000000105",
        "Cari_Unvan": "Kaya Matbaacılık ve Ambalaj",
        "Tarih": "2026-09-12",
        "Tutar": 31450.75,
        "Durum": "Hatalı",
        "Hata_Kodu": "ERR_MATH_02",
        "Hata_Aciklamasi": "Satır toplamları ile dip genel toplam kuruş farkı nedeniyle uyuşmuyor."
    },
    {
        "Fatura_No": "GIB2026000000106",
        "Cari_Unvan": "Anadolu Kağıt Ürünleri Ltd.",
        "Tarih": "2026-09-13",
        "Tutar": 9200.00,
        "Durum": "Onaylandı",
        "Hata_Kodu": "-",
        "Hata_Aciklamasi": "Başarılı."
    }
]

df = pd.DataFrame(data)
df.to_excel("logo_faturalar.xlsx", index=False)
print("logo_faturalar.xlsx başarıyla oluşturuldu!")