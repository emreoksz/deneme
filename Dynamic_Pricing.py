import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_csv("C:/Users/EyupcanGuven/Desktop/pricing.csv", sep=";")
df = df_.copy()

df.head()
df.info()
# 1 - Item'in fiyatı kategorilere göre farklılık göstermekte
# midir? İstatistiki olarak ifade ediniz.

df.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T
df.shape
df["category_id"].nunique()
df.isnull().sum()

df.groupby("category_id").agg({"price": ["mean"]})
#Medyan uzerinden gidilmesine karar verildi
#Farklılıklar anlamlı mı degil mi? Her kategori icin ayrı ayrı bakılır

# Aykırı degerlerden kurtulma:


def outlier_thresholds(dataframe, variable, low_quantile=0.05, up_quantile=0.95):
    quantile_one = dataframe[variable].quantile(low_quantile)
    quantile_three = dataframe[variable].quantile(up_quantile)
    interquantile_range = quantile_three - quantile_one
    up_limit = quantile_three + 1.5 * interquantile_range
    low_limit = quantile_one - 1.5 * interquantile_range
    return low_limit, up_limit


def has_outliers(dataframe, numeric_columns):
    for col in numeric_columns:
        low_limit, up_limit = outlier_thresholds(dataframe, col)
        if dataframe[(dataframe[col] > up_limit) | (dataframe[col] < low_limit)].any(axis=None):
            number_of_outliers = dataframe[(dataframe[col] > up_limit) | (dataframe[col] < low_limit)].shape[0]
            print(col, " : ", number_of_outliers, "outliers")


def remove_outliers(dataframe, numeric_columns):
    for variable in numeric_columns:
        low_limit, up_limit = outlier_thresholds(dataframe, variable)
        dataframe_without_outliers = dataframe[~((dataframe[variable] < low_limit) | (dataframe[variable] > up_limit))]
    return dataframe_without_outliers


remove_outliers(df,["price"])
has_outliers(df,["price"])


# Kategorilerin her birinin ikili olarak test edilmesi
# Varsayımların uygulanması:

############################
# 1.1 Normallik Varsayımı
############################

# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1:..sağlanmamaktadır.

from scipy.stats import shapiro


#Normallik varsayımına bakıldı
print(" Shapiro-Wilks Test Result")
for category in df["category_id"].unique():
    test_statistic , pvalue = shapiro(df.loc[df["category_id"] == category, "price"])
    if(pvalue<0.05):
        print('\n','{0} -> '.format(category),'Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue),"H0 is rejected.")
    else:
         print('Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue),"H0 is not rejected.")

# Output:

 #Shapiro-Wilks Test Result
 #489756 ->  Test statistic = 0.1095, p-Value = 0.0000 H0 is rejected.
 #361254 ->  Test statistic = 0.0615, p-Value = 0.0000 H0 is rejected.
 #874521 ->  Test statistic = 0.1311, p-Value = 0.0000 H0 is rejected.
 #326584 ->  Test statistic = 0.0568, p-Value = 0.0000 H0 is rejected.
 #675201 ->  Test statistic = 0.1011, p-Value = 0.0000 H0 is rejected.
 #201436 ->  Test statistic = 0.6190, p-Value = 0.0000 H0 is rejected.

# Eğer normallik sağlanmadıgından nonparametrik test yapacağız (mannwhitneyu testi)


# mannwhitneyu testi (non-parametrik test)

import scipy.stats as stats
import itertools

# Test İstatistiği:
# H0: İki kategori için ödenen medyan fiyat arasında farklılık yoktur.
# H1: İki kategori için ödenen medyan fiyat arasında farklılık vardır.

combine = []

for i in itertools.combinations(df["category_id"].unique(), 2):
    combine.append(i)
combine
for i in combine:
    test_statistic, pvalue = stats.mannwhitneyu(df.loc[df["category_id"] == i[0], "price"],
                                                df.loc[df["category_id"] == i[1], "price"])
    if pvalue < 0.05:

        print(f"{i[0]} - {i[1]} -> ", "Test statistic = %.4f, p-value = %.4f" % (test_statistic, pvalue),
              "H0 red edilir")
    else:

        print(f"{i[0]} - {i[1]} -> ", "Test statistic = %.4f, p-value = %.4f" % (test_statistic, pvalue),
              "H0 red edilemez")


print('Test İstatistiği = %.4f, p-değeri = %.4f' % (test_statistic, pvalue))

#489756 hepsinden farklıdır
#326584 hepsinden farklıdır
#874521, 675201, 201436, 361254 farklılık yoktur

# İtemin fiyatı kategorilere göre farklılık göstermekte midir?
# 10 kategorik çift medyan fiyat arasında farklılık var.
# 5 kategorik çift medyan fiyat arasında farklılık yoktur.

# 2- İlk soruya bağlı olarak item'ın fiyatı ne olmalıdır?
# Nedenini açıklayınız?

# 489756 ve 326584 için ayrı ayrı medyan degerleri fiyat olarak belirlenebilir

df.loc[df["category_id"] == 489756, "price"].median()
# fiyat: 35.635784234

df.loc[df["category_id"] == 326584, "price"].median()
# fiyat: 31.7482419128


# Digerleri icin ortalama medyan degerlerinin ortalaması fiyat olarak belirlenebilir
fancy = [675201, 201436, 874521, 361254]

top = []
for i in fancy:
    top.append(df.loc[df["category_id"] == i, "price"].median())


#Farklı olmayanların medyan fiyatı:
sum(top)/len(top)
#34.057574562275


# 3- Fiyat konusunda "hareket edebilir olmak" istenmektedir.
# Fiyat stratejisi için karar destek sistemi oluşturunuz.


import statsmodels.stats.api as sms
sms.DescrStatsW(top).tconfint_mean()



# 4- Olası fiyat değişiklikleri için item satın almalarını ve
# gelirlerini simüle ediniz.

# 489756 ve 326584 için ayrı ayrı medyan degerleri fiyat olarak belirlenebilir
# 489756
freq = df[df["category_id"] == 489756].count()[0]
income = freq*35.635784234
print("Income: ", income)

# 326584
freq = df[df["category_id"] == 326584].count()[0]
income = freq*31.7482419128
print("Income: ", income)


# conf interval min
freq = 0
for i in [675201, 201436, 874521, 361254]:
    freq += df[df["category_id"] == i].count()[0]

income = freq*33.344860323448636
print("Income: ", income)

# conf interval max

freq = 0
for i in [675201, 201436, 874521, 361254]:
    freq += df[df["category_id"] == i].count()[0]

income = freq*34.770288801101366
print("Income: ", income)

# average : 34.057574562275

freq = 0
for i in [675201, 201436, 874521, 361254]:
    freq += df[df["category_id"] == i].count()[0]

income = freq * 34.057574562275
print("Income: ", income)




