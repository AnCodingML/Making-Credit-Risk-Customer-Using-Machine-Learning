# -*- coding: utf-8 -*-
"""vix-2-idx-partner (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CBhYIt5wv_NkxCAeIATj54T-DrDXeJNj
"""

# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All"
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import QuantileTransformer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

dataset_path = '/kaggle/input/loandataset/loan_data_2007_2014.csv'
# Baca dataset menggunakan Pandas
df = pd.read_csv(dataset_path)

"""# Business Understanding

Kita sebagai seorang Datascience diminta untuk membuat model yang dapat memprediksi credit risk customer tersebut untuk menghindari kerugian perusahaan. Dataset terdiri dari berbagai customer yang sudah melakukan peminjaman beserta informasi kondisi kredit setiap customernya.<br><br>
*Goals* <br>
Membuat model yang dapat memprediksi credit risk customer tersebut untuk menghindari kerugian perusahaan<br>
*obejective*<br>
1. Menentukan data yang digunakan untuk modeling
2. Membuat segmentasi customer berdasarkan credit risk <br>

*Business Metrics*<br>
credit risk

# Dataset Collection
"""

pd.set_option('display.max_columns', 500)

df.head(2)

"""Karena model yang dibuat adalah model untuk memprediksi credit risk cutomer, maka kolom kondisi customer setelah melakukan peminjaman di drop."""

x = ['id','member_id','acc_now_delinq','addr_state','annual_inc','application_type',
     'collection_recovery_fee','collections_12_mths_ex_med','delinq_2yrs','desc','emp_length','emp_title','funded_amnt',
     'grade','sub_grade','home_ownership','initial_list_status','installment','int_rate','issue_d','loan_status','pub_rec',
     'purpose','term','title','url','zip_code']
df= df[x]

"""# Exploratory Data Analysis"""

df.info()

"""Dataset memiliki 466285 baris  dan memiliki 37 kolom, dataset memiliki 2 kolom identitas yaitu id dan member_id."""

# Menghitung jumlah nilai null pada setiap kolom
jumlah_null = df.isnull().sum()

# Mengurutkan jumlah nilai null secara menurun
urutan_null = jumlah_null.sort_values(ascending=True)

# Mengambil 10 kolom dengan nilai null terbanyak
top_10_null = urutan_null.tail(30)

# Membuat grafik batang
plt.figure(figsize=(10, 6))
top_10_null.plot(kind='barh')
plt.title('Kolom dengan Nilai Null')
plt.xlabel('Kolom')
plt.ylabel('Jumlah Nilai Null')
#plt.xticks(rotation=45)
plt.show()

"""Pada dataset, terdapat beberapa kolom yang memiliki nilai kosong dengan jumlah cukup banyak dan ada beberapa kolom yang sama sekali tidak memiliki nilai didalamnya, hal ini harus ditinjau lebih lanjut untuk menangani banyak nilai kosong pada dataset."""

df.duplicated().sum()

"""Data tidak memiliki nilai duplikat.

## Analisis Univariate dan Bivariate

### Univariate

#### Numeric
"""

df.describe().T

# Mengambil kolom dengan jenis numerik
kolom_numerik = df.select_dtypes(include='number')
drop = ['member_id','id']
kolom_numerik = kolom_numerik.drop(drop, axis=1)
# Melakukan plot untuk melihat skewness data
for kolom in kolom_numerik.columns:
    sns.displot(df[kolom], kde=True)
    plt.title(f'Distribusi data {kolom}')
    plt.show()

# Membuat box plot untuk setiap kolom numerik
for kolom in kolom_numerik.columns:
    sns.boxplot(x=df[kolom])
    plt.title(f'Box Plot {kolom}')
    plt.show()

"""#### Categorical"""

x = df.select_dtypes(include='object')
for kolom in x.columns:
    print(kolom + ":")
    print(x[kolom].nunique())

"""kolom dengan high cardinality :
1. desc
2. url
3. emp_title
4. title
5. zip_code

kolo dengan nilai tunggal :
1. application_type
"""

kolom_kategorikal = df.select_dtypes(include='object')
kolom_kategorikal.value_counts()
drop = ['desc','url','emp_title','title','zip_code','application_type']
kolom_kategorikal = kolom_kategorikal.drop(drop, axis=1)

kolom_kategorikal['issue_d']= kolom_kategorikal['issue_d'].str[:3]
kolom_kategorikal.head(4)

# Membuat grafik kategori untuk setiap kolom
for kolom in kolom_kategorikal.columns:
    plt.figure(figsize=(10, 6))
    kolom_plot = kolom_kategorikal[kolom].value_counts().plot(kind='bar')
    kolom_plot.set_title(f'Grafik Kategori {kolom}')
    kolom_plot.set_xlabel('Kategori')
    kolom_plot.set_ylabel('Jumlah')
    plt.show()

"""### Bivariate

#### Categorical & Categorical
"""

x = kolom_kategorikal.drop('loan_status', axis=1)
# Mengambil kolom-kolom lainnya
kolom_lainnya = x
hue_order = ['Charged Off', 'Default', 'Does not meet the credit policy. Status:Charged Off',
             'Late (31-120 days)', 'Late (16-30 days)', 'In Grace Period']

for kolom in kolom_lainnya.columns:
    plt.figure(figsize=(10, 6))
    sns.countplot(x=kolom, data=kolom_kategorikal, hue='loan_status')
    plt.title(f'Grafik Kategori {kolom} dengan Loan_Status')
    plt.xlabel('Kategori')
    plt.ylabel('Jumlah')
    plt.xticks(rotation=90)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

"""#### Numeric & Numeric"""

# Menghitung matriks korelasi
corr_matrix = df.corr()

# Membuat heatmap untuk matriks korelasi
plt.figure(figsize=(20, 20))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Map')
plt.show()

"""#### Multivarite"""

df.info()

kolom_numerik

kolom_kategorikal

# Membuat scatter plot dengan hue berdasarkan kolom "category"
sns.scatterplot(data=df, x='grade', y='annual_inc', hue='loan_status',hue_order = hue_order)

# Menampilkan grafik
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xticks(rotation=90)
plt.ylim(0, 2000000)
plt.show()

# Membuat scatter plot dengan hue berdasarkan kolom "category"
sns.scatterplot(data=df, x='emp_length', y='annual_inc', hue='loan_status',hue_order = hue_order)

# Menampilkan grafik
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xticks(rotation=90)
plt.ylim(0, 2000000)
plt.show()

"""# Feature Engineering

## segmentasi wilayah
"""

df['addr_state'].unique()

# Data array berisi kode negara
data = df['addr_state']

# Membuat dataframe dengan kolom 'addr_state' dari data array
s = pd.DataFrame(data, columns=['addr_state'])

# Fungsi untuk mengelompokkan kualitas negara berdasarkan kode negara
def get_quality(state):
    high_quality = ['CA', 'MA', 'WA', 'NY', 'VA']
    medium_quality = ['CO', 'OR', 'MN', 'UT', 'IL', 'WI', 'MD', 'CT', 'NJ']

    if state in high_quality:
        return 'Kualitas Tinggi'
    elif state in medium_quality:
        return 'Kualitas Menengah'
    else:
        return 'Kualitas Rendah'

# Membuat kolom baru 'Kualitas Negara' dengan menerapkan fungsi get_quality pada setiap baris kode negara
df['Kualitas_Negara'] = s['addr_state'].apply(get_quality)

df['purpose'].unique()

# Fungsi untuk melakukan segmentasi kategori pinjaman
def segment_loan_purpose(purpose):
    personal_categories = ['credit_card', 'car', 'small_business', 'other']
    major_expense_categories = ['wedding', 'debt_consolidation', 'home_improvement', 'major_purchase']
    special_purpose_categories = ['medical', 'moving', 'vacation', 'house']

    if purpose in personal_categories:
        return 'Personal'
    elif purpose in major_expense_categories:
        return 'Major Expense'
    elif purpose in special_purpose_categories:
        return 'Special Purpose'
    else:
        return 'Other'

# Menambahkan kolom baru 'Segmented Purpose' yang melakukan segmentasi pada setiap baris data
df['Segmented Purpose'] = df['purpose'].apply(segment_loan_purpose)

df.info()

"""## Defining Label"""

# Daftar status yang akan diubah menjadi 0 (Current dan Fully Paid)
status_to_zero = ['Current', 'Fully Paid','Does not meet the credit policy. Status:Fully Paid']

# Mengganti status menjadi 0 atau 1 berdasarkan kondisi
df['loan_status'] = df['loan_status'].replace(status_to_zero, 0)
df['loan_status'] = df['loan_status'].replace({status: 1 for status in df['loan_status'].unique() if status != 0})

"""## Handling Date Column"""

df['issue_d']= df['issue_d'].str[:3]

"""## Drop Column"""

drop = ['addr_state','purpose']
df = df.drop(drop, axis=1)

"""### Drop High Cardinality"""

drop = ['desc','url','emp_title','title','zip_code']
df = df.drop(drop, axis=1)

"""### Drop Low Cardinality"""

drop = ['application_type']
df = df.drop(drop, axis=1)

"""### Drop Columns Identity"""

drop = ['member_id','id']
df = df.drop(drop, axis=1)

"""### Drop Redundant Columns"""

drop = ['sub_grade','funded_amnt']
df = df.drop(drop, axis=1)

"""### Drop Null Values"""

df.dropna(subset=['emp_length'],axis=0, inplace=True)
df.dropna(subset=['collections_12_mths_ex_med'],axis=0, inplace=True)

"""### Drop Duplicate"""

df.drop_duplicates(inplace=True)

"""# Data Preprocessing"""

df.head(2)

"""## Transformasi Data Numerik"""

data_skew = df.select_dtypes(include='number')

scaler = QuantileTransformer()
df[data_skew.columns] =scaler.fit_transform(df[data_skew.columns])

"""## Transformasi Data Categorical

### Label Encoding
"""

def label_encoding_with_changes(data):
    encoder = LabelEncoder()
    encoded_data = encoder.fit_transform(data)
    mapping = {label: encoded_label for label, encoded_label in zip(data, encoded_data)}

    print("Original Value\t|\tEncoded Value")
    print("----------------|---------------")
    for label, encoded_label in mapping.items():
        print(f"{label}\t\t|\t{encoded_label}")

    return encoded_data


data = df['emp_length']
df['emp_length'] = label_encoding_with_changes(data)
data = df['grade']
df['grade'] = label_encoding_with_changes(data)
data = df['term']
df['term'] = label_encoding_with_changes(data)
data = df['Kualitas_Negara']
df['Kualitas_Negara'] = label_encoding_with_changes(data)

df['emp_length'].value_counts()

df['emp_length'] = df['emp_length'].replace({1: 10, 10: 1})

"""### One Hot-encoding"""

df.head(3)

x = df

x = x.select_dtypes(include='object')

df_encoded = pd.get_dummies(x, columns=x.columns)

df_encoded

df.head(3)

dataset = df.drop(df.select_dtypes(include='object').columns, axis=1)

dataset = pd.concat([dataset, df_encoded], axis=1)

dataset

"""## Handling Imbalance

## Split Dataset
"""

!pip install imblearn

X = dataset.drop('loan_status', axis=1)
y = dataset['loan_status']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

y_train_resampled.value_counts()

"""# Modeling"""

!pip install xgboost

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from sklearn.model_selection import cross_validate
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
import xgboost as xgb


def eval_classification(model):
    y_pred = model.predict(X_test)
    y_pred_train = model.predict(X_train)
    y_pred_proba = model.predict_proba(X_test)
    y_pred_proba_train = model.predict_proba(X_train)

    print("Accuracy (Test Set): %.2f" % accuracy_score(y_test, y_pred))
    print("Precision (Test Set): %.2f" % precision_score(y_test, y_pred))
    print("Recall (Test Set): %.2f" % recall_score(y_test, y_pred))
    print("F1-Score (Test Set): %.2f" % f1_score(y_test, y_pred))

    print("roc_auc (test-proba): %.2f" % roc_auc_score(y_test, y_pred_proba[:, 1]))
    print("roc_auc (train-proba): %.2f" % roc_auc_score(y_train, y_pred_proba_train[:, 1]))
    #
    # score = cross_validate(model, X, y, cv=5, scoring='roc_auc', return_train_score=True)
    # print('roc_auc (crossval train): '+ str(score['train_score'].mean()))
    # print('roc_auc (crossval test): '+ str(score['test_score'].mean()))

def grafik_roc_auc(model):
    # predict probabilities of positive class for training and testing data
    y_train_prob = model.predict_proba(X_train)[:, 1]
    y_test_prob = model.predict_proba(X_test)[:, 1]

    # calculate ROC AUC score for training and testing data
    train_auc = roc_auc_score(y_train, y_train_prob)
    test_auc = roc_auc_score(y_test, y_test_prob)

    # calculate false positive rate and true positive rate for training and testing data
    train_fpr, train_tpr, _ = roc_curve(y_train, y_train_prob)
    test_fpr, test_tpr, _ = roc_curve(y_test, y_test_prob)

    # create dataframe to store ROC data
    roc_data = pd.DataFrame({
    'FPR (Train)': train_fpr,
    'TPR (Train)': train_tpr,
    'FPR (Test)': test_fpr,
    'TPR (Test)': test_tpr
    })

    # plot ROC curves for training and testing data
    plt.plot(train_fpr, train_tpr, label=f'Train ROC curve (AUC = {train_auc:.2f})')
    plt.plot(test_fpr, test_tpr, label=f'Test ROC curve (AUC = {test_auc:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.show()


def show_feature_importance(model):
    feat_importances = pd.Series(model.feature_importances_, index=X.columns)
    ax = feat_importances.nlargest(25).plot(kind='barh', figsize=(10, 8))
    ax.invert_yaxis()

    plt.xlabel('score')
    plt.ylabel('feature')
    plt.title('feature importance score')

def show_best_hyperparameter(model):
    print(model.best_estimator_.get_params())

from sklearn.ensemble import AdaBoostClassifier

ada = AdaBoostClassifier(random_state=42)

ada.fit(X_train, y_train)
y_pred = ada.predict(X_test)
eval_classification(ada)

from sklearn.ensemble import RandomForestClassifier

rfc = RandomForestClassifier(random_state=42)
rfc.fit(X_train, y_train)
y_pred = rfc.predict(X_test)
eval_classification(rfc)

import xgboost as xgb

# Buat model XGBoost
xgb_model = xgb.XGBClassifier(random_state=42)

# Latih model menggunakan data training
xgb_model.fit(X_train, y_train)

# Prediksi data testing
y_pred = xgb_model.predict(X_test)
eval_classification(xgb_model)

from sklearn.ensemble import GradientBoostingClassifier

gb_model = GradientBoostingClassifier(random_state=42)



# Latih model menggunakan data training
gb_model.fit(X_train, y_train)

# Prediksi data testing
y_pred = gb_model.predict(X_test)
eval_classification(gb_model)

'''from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RandomizedSearchCV

gb_classifier = GradientBoostingClassifier()

# Daftar hyperparameter yang akan diuji
param_distributions = {
    'n_estimators': np.arange(50, 201, 50),
    'learning_rate': [0.01, 0.1, 0.5],
    'max_depth': [3, 5, 7]
}

# Inisialisasi RandomizedSearch dengan model dan hyperparameter yang telah ditentukan
random_search = RandomizedSearchCV(estimator=gb_classifier, param_distributions=param_distributions,
                                   scoring='roc_auc', n_iter=10, cv=5, random_state=42)

# Lakukan hyperparameter tuning menggunakan RandomizedSearch dengan data latih
random_search.fit(X_train, y_train)

# Cetak hasil hyperparameter tuning terbaik
print("Best Hyperparameters:", random_search.best_params_)
print("Best ROC AUC Score:", random_search.best_score_)

# Gunakan model terbaik untuk melakukan prediksi pada data uji
best_gb_classifier = random_search.best_estimator_
y_pred = best_gb_classifier.predict(X_test)

# Hitung ROC AUC Score pada data uji
roc_auc = roc_auc_score(y_test, y_pred)
print("ROC AUC Score on Test Data:", roc_auc)'''

show_feature_importance(ada)

from sklearn.ensemble import AdaBoostClassifier

ada = AdaBoostClassifier(random_state=42)

ada.fit(X, y)
df['predic'] = ada.predict(X)

df

x = df[['loan_status']]
x['predic'] = df['predic']

x

"""# Model Testing"""

x[x['loan_status']==1].value_counts()

x[x['loan_status']==0].value_counts()