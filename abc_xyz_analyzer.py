import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def classify_abc_xyz(df):
    """
    df kolonları: 'SKU', 'Annual_Value', 'Demand_History' (aylık talep listesi)
    """
    # 1. ABC Sınıflandırması (Kümülatif Değer Yüzdesi)
    df = df.sort_values(by="Annual_Value", ascending=False).reset_index(drop=True)
    df["Cum_Value_Pct"] = (df["Annual_Value"].cumsum() / df["Annual_Value"].sum()) * 100
    
    def assign_abc(pct):
        if pct <= 80:
            return 'A'
        elif pct <= 95:
            return 'B'
        else:
            return 'C'
            
    df["ABC"] = df["Cum_Value_Pct"].apply(assign_abc)
    
    # 2. XYZ Sınıflandırması (Değişim Katsayısı - CV = std / mean)
    def calculate_cv(demands):
        arr = np.array(demands)
        mean_val = np.mean(arr)
        if mean_val == 0:
            return 1.0
        return np.std(arr) / mean_val
        
    df["CV"] = df["Demand_History"].apply(calculate_cv)
    
    def assign_xyz(cv):
        if cv < 0.25:
            return 'X'
        elif cv < 0.50:
            return 'Y'
        else:
            return 'Z'
            
    df["XYZ"] = df["CV"].apply(assign_xyz)
    df["Class"] = df["ABC"] + df["XYZ"]
    
    return df

def plot_matrix_heatmap(df):
    """3x3 Matris frekans tablosu ve ısı haritası."""
    matrix = pd.crosstab(df["ABC"], df["XYZ"], reindex=True).reindex(index=['A', 'B', 'C'], columns=['X', 'Y', 'Z'], fill_value=0)
    
    fig, ax = plt.subplots(figsize=(8, 7))
    cax = ax.matshow(matrix.values, cmap='Blues', alpha=0.85)
    
    # Hücre içi sayıları ve etiketleri yaz
    strategies = {
        ('A', 'X'): "JIT / Sürekli Akış",
        ('A', 'Y'): "Sıkı Güvenlik Stoğu",
        ('A', 'Z'): "Sipariş Üzerine (MTO)",
        ('B', 'X'): "Standart ROP / EOQ",
        ('B', 'Y'): "Dönemsel Gözden Geçirme",
        ('B', 'Z'): "Tampon Stok",
        ('C', 'X'): "Toplu Satın Alma",
        ('C', 'Y'): "İki Kutulu Sistem",
        ('C', 'Z'): "Minimum Sipariş / Spot"
    }
    
    for i, row in enumerate(['A', 'B', 'C']):
        for j, col in enumerate(['X', 'Y', 'Z']):
            val = matrix.loc[row, col]
            strat = strategies.get((row, col), "")
            ax.text(j, i, f"{row}{col}\n({val} SKU)\n\n{strat}", 
                    ha='center', va='center', color='black', fontweight='bold', fontsize=9)
                    
    fig.colorbar(cax)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xticklabels(['X (CV < 0.25)\nKararlı', 'Y (0.25 ≤ CV < 0.50)\nDeğişken', 'Z (CV ≥ 0.50)\nÖngörülemez'], fontsize=10)
    ax.set_yticklabels(['A (İlk %80 Değer)', 'B (Sonraki %15)', 'C (Kalan %5)'], fontsize=10)
    
    ax.set_title("ABC-XYZ 9'lu Envanter Segmentasyon Matrisi", fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig("abc_xyz_matrix.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    np.random.seed(42)
    sample_data = []
    for i in range(1, 401):
        ann_val = np.random.exponential(scale=5000)
        demands = np.random.poisson(lam=np.random.randint(10, 100), size=12)
        sample_data.append({"SKU": f"SKU-{i:03d}", "Annual_Value": ann_val, "Demand_History": demands})
        
    df_sample = pd.DataFrame(sample_data)
    classified_df = classify_abc_xyz(df_sample)
    print("Sınıflandırma Özeti:\n", classified_df["Class"].value_counts())
    plot_matrix_heatmap(classified_df)
