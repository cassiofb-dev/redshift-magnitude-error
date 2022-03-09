# -*- coding: utf-8 -*-
"""mag_err_corr.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1n3OysQtDd2E7vQMbvRhXUjIZSsXtQBap

# Instalando Pacotes
"""

import subprocess

def install(package):
  install_process = subprocess.run(
    [
      'pip',
      'install',
      '--upgrade',
      package,
    ],
  )

PACKAGES = [
  'numpy',
  'scipy',
  'pandas',
  'seaborn',
  'xgboost',
  'scikit-learn',
  'https://github.com/pandas-profiling/pandas-profiling/archive/master.zip',
]

for package in PACKAGES:
  install(package)

"""# Importes"""

import os, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

from urllib import request
from statistics import mean

from time import perf_counter

import seaborn as sns

from scipy import stats

from sklearn.metrics import mean_squared_error

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

from sklearn.multioutput import MultiOutputRegressor

from sklearn.neural_network import MLPRegressor

from sklearn.neighbors import KNeighborsRegressor

from sklearn.ensemble import RandomForestRegressor

from xgboost import XGBRegressor

from pandas_profiling import ProfileReport

sns.set_theme()
sns.set_theme(font_scale=2)

"""# Estrutura de Pastas"""

DOWNLOADS_FOLDER = 'downloads'
DATASETS_FOLDER = 'datasets'
PROFILES_FOLDER = 'profiles'
RESULTS_FOLDER = 'results'
IMAGES_FOLDER = 'images'

FOLDERS = [
  DOWNLOADS_FOLDER,
  DATASETS_FOLDER,
  PROFILES_FOLDER,
  RESULTS_FOLDER,
  IMAGES_FOLDER,
]

for folder in FOLDERS:
  try: os.mkdir(folder)
  except: print(f"folder ({folder}) already exists.")

"""# Constantes

## Bancos de Dados
"""

OUTLIER_ZSCORE_THRESHOLD = 3

TEDDY_DATASETS_URL = [
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Teddy/forTemplateBased/teddyT_A.cat',
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Teddy/forTemplateBased/teddyT_B.cat',
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Teddy/forTemplateBased/teddyT_C.cat',
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Teddy/forTemplateBased/teddyT_D.cat',
]

HAPPY_DATASETS_URL = [
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Happy/forTemplateBased/happyT_A',
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Happy/forTemplateBased/happyT_B',
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Happy/forTemplateBased/happyT_C',
  'https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Happy/forTemplateBased/happyT_D',
]

SDSS_DATASETS_URL = [
  'https://zenodo.org/record/4291181/files/sdss_train_data.csv?download=1',
]

DATASETS = [
  {
    'name': 'teddy',
    'urls': TEDDY_DATASETS_URL,
    'header': 'infer',
    'index_col': False,
  },
  {
    'name': 'happy',
    'urls': HAPPY_DATASETS_URL,
    'header': 'infer',
    'index_col': False,
  },
  {
    'name': 'sdss',
    'urls': SDSS_DATASETS_URL,
    'header': 0,
    'index_col': False,
  },
]

"""## Modelos"""

# MODEL INPUT AND OUTPUT
X_FEATURE_COLUMNS = [letter for letter in 'ugriz']
Y_TARGET_COLUMNS  = [column + 'Err' for column in X_FEATURE_COLUMNS]

# MODEL CONFIG
RANDOM_STATE = 0
USE_ALL_CPU_CORES = -1
TEST_TRAIN_SPLIT_RATIO = 1 / 5
CROSS_VALIDATION_FOLDS = 5
PARALLEL_JOBS = USE_ALL_CPU_CORES

# RANDOM FOREST MODEL CONFIG
# https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
RANDOM_FOREST_HYPERPARAMETER_GRID = {
  'n_estimators': [1, 10, 50],
  'max_depth'   : [5, 10],
  # 'criterion'   : ['squared_error'],
}

RANDOM_FOREST_GRID_SEARCH_CV = GridSearchCV(
  estimator  = RandomForestRegressor(random_state = RANDOM_STATE),
  param_grid = RANDOM_FOREST_HYPERPARAMETER_GRID,
  cv         = CROSS_VALIDATION_FOLDS,
  n_jobs     = PARALLEL_JOBS,
)

# MLP MODEL CONFIG
# https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html
MLP_HYPERPARAMETER_GRID = {
  'hidden_layer_sizes': [(5), (10), (5,5)],
  # 'activation': ['relu'],
  # 'solver': ['adam'],
  'max_iter': [100, 500],
}

MLP_GRID_SEARCH_CV = GridSearchCV(
  estimator  = MLPRegressor(random_state = RANDOM_STATE),
  param_grid = MLP_HYPERPARAMETER_GRID,
  cv         = CROSS_VALIDATION_FOLDS,
  n_jobs     = PARALLEL_JOBS,
)

# KNN MODEL CONFIG
# https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html
KNN_HYPERPARAMETER_GRID = {
  'n_neighbors': [1, 5, 10],
  'weights'    : ['uniform', 'distance'],
}

KNN_GRID_SEARCH_CV = GridSearchCV(
  estimator  = KNeighborsRegressor(),
  param_grid = KNN_HYPERPARAMETER_GRID,
  cv         = CROSS_VALIDATION_FOLDS,
  n_jobs     = PARALLEL_JOBS,
)

# XGB MODEL CONFIG
# https://xgboost.readthedocs.io/en/stable/index.html
XGB_HYPERPARAMETER_GRID = {
  'max_depth'   : [1, 5, 10],
  'objective'   : ['reg:squarederror'],
}

XGB_GRID_SEARCH_CV = GridSearchCV(
  estimator  = XGBRegressor(),
  param_grid = XGB_HYPERPARAMETER_GRID,
  cv         = CROSS_VALIDATION_FOLDS,
  n_jobs     = PARALLEL_JOBS,
)

# XGB MODEL CONFIG SUPPORT FOR MULTIPLE OUTPUTS
XGB_MULTI_OUTPUT_HYPERPARAMETER_GRID = {
  'estimator__max_depth'   : [5, 10],
  'estimator__objective'   : ['reg:squarederror'],
}

XGB_MULTI_OUTPUT_GRID_SEARCH_CV = GridSearchCV(
  estimator  = MultiOutputRegressor(XGBRegressor()),
  param_grid = XGB_MULTI_OUTPUT_HYPERPARAMETER_GRID,
  cv         = CROSS_VALIDATION_FOLDS,
  n_jobs     = PARALLEL_JOBS,
)

# ALL GRID SEARCH CVS
MODELS = [
  {
    'name': 'RANDOM_FOREST',
    'grid_search_cv': RANDOM_FOREST_GRID_SEARCH_CV,
    'support_multiple_output': True,
  },
  {
    'name': 'MLP',
    'grid_search_cv': MLP_GRID_SEARCH_CV,
    'support_multiple_output': True,
  },
  {
    'name': 'KNN',
    'grid_search_cv': KNN_GRID_SEARCH_CV,
    'support_multiple_output': True,
  },
  {
    'name': 'XGB',
    'grid_search_cv': XGB_GRID_SEARCH_CV,
    'multi_output_grid_search_cv': XGB_MULTI_OUTPUT_GRID_SEARCH_CV,
    'support_multiple_output': False,
  },
]

"""# Funções

## Bancos de Dados
"""

def load_dataset(dataset_url, dataset_name, header, index_col):
  dataset_download_path = f"{DOWNLOADS_FOLDER}/{dataset_name}.csv"

  if os.path.isfile(dataset_download_path) == False:
    request.urlretrieve(dataset_url, dataset_download_path)

  dataset_df = pd.read_csv(
      dataset_download_path,
      comment = '#',
      names   = ['ID', *X_FEATURE_COLUMNS, *Y_TARGET_COLUMNS],
      sep     = '\s+|,',
      engine  = 'python',
      header  = header,
      index_col = index_col,
  )

  return dataset_df

def load_dataset_urls(dataset):
  full_df = pd.concat([
    load_dataset(
      dataset_url,
      dataset['name'] + '_' + str(index),
      dataset['header'],
      dataset['index_col'],
    ) for (index, dataset_url) in enumerate(dataset['urls'])
  ])

  full_df.reset_index(drop=True, inplace=True)
  full_df.to_csv(f"{DATASETS_FOLDER}/{dataset['name']}.raw.csv")

  sns.pairplot(
    full_df,
    x_vars=X_FEATURE_COLUMNS,
    y_vars=X_FEATURE_COLUMNS,
  ).savefig(f"{IMAGES_FOLDER}/{dataset['name']}_bands_vs_bands.raw.png")

  sns.pairplot(
    full_df,
    x_vars=Y_TARGET_COLUMNS,
    y_vars=Y_TARGET_COLUMNS,
  ).savefig(f"{IMAGES_FOLDER}/{dataset['name']}_errors_vs_errors.raw.png")

  sns.pairplot(
    full_df,
    x_vars=X_FEATURE_COLUMNS,
    y_vars=Y_TARGET_COLUMNS,
  ).savefig(f"{IMAGES_FOLDER}/{dataset['name']}_bands_vs_errors.raw.png")

  profile_name = f"{dataset['name']}.raw.analysis".lower()
  profile = ProfileReport(full_df, title=profile_name, explorative=True)
  profile.to_file(f"{PROFILES_FOLDER}/{profile_name}.html")

  no_duplicate_df = full_df.drop_duplicates()

  no_duplicate_df = no_duplicate_df[[*X_FEATURE_COLUMNS, *Y_TARGET_COLUMNS]]

  outlier_mask = (np.abs(stats.zscore(no_duplicate_df)) < OUTLIER_ZSCORE_THRESHOLD).all(axis=1)

  no_outlier_df = no_duplicate_df[outlier_mask]
  outlier_df = no_duplicate_df[~outlier_mask]

  outlier_df.reset_index(drop=True, inplace=True)
  outlier_df.to_csv(f"{DATASETS_FOLDER}/{dataset['name']}.outlier.csv")

  processed_df = no_outlier_df.transform('log2')

  processed_df.reset_index(drop=True, inplace=True)
  processed_df.to_csv(f"{DATASETS_FOLDER}/{dataset['name']}.processed.csv")

  sns.pairplot(
    processed_df,
    x_vars=X_FEATURE_COLUMNS,
    y_vars=X_FEATURE_COLUMNS,
  ).savefig(f"{IMAGES_FOLDER}/{dataset['name']}_bands_vs_bands.processed.png")

  sns.pairplot(
    processed_df,
    x_vars=Y_TARGET_COLUMNS,
    y_vars=Y_TARGET_COLUMNS,
  ).savefig(f"{IMAGES_FOLDER}/{dataset['name']}_errors_vs_errors.processed.png")

  sns.pairplot(
    processed_df,
    x_vars=X_FEATURE_COLUMNS,
    y_vars=Y_TARGET_COLUMNS,
  ).savefig(f"{IMAGES_FOLDER}/{dataset['name']}_bands_vs_errors.processed.png")

  profile_name = f"{dataset['name']}.processed.analysis".lower()
  profile = ProfileReport(processed_df, title=profile_name, explorative=True)
  profile.to_file(f"{PROFILES_FOLDER}/{profile_name}.html")

  return processed_df

def split_feature_target(dataset_df):
  X = dataset_df[X_FEATURE_COLUMNS]
  y = dataset_df[Y_TARGET_COLUMNS]

  return X, y

def split_train_test(X, y):
  X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    random_state = 0,
    test_size    = TEST_TRAIN_SPLIT_RATIO,
  )

  return X_train, X_test, y_train, y_test

def load_split_dataset(dataset):
  dataset_df = load_dataset_urls(dataset)

  X, y = split_feature_target(dataset_df)

  X_train, X_test, y_train, y_test = split_train_test(X, y)

  return X_train, X_test, y_train, y_test

"""## Código Auxiliar para Tabela e Log"""

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DataFrame DataTable</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js" integrity="sha512-894YE6QWD5I59HgZOGReFYm4dnWc1Qt5NtvYSaNcOP+u1T9qYdvdihz0PPSiiqn/+/3e7Jo4EaG7TubfWGUrMQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script src="https://cdn.datatables.net/1.11.4/js/jquery.dataTables.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <link rel="stylesheet" href="https://cdn.datatables.net/1.11.4/css/jquery.dataTables.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />
</head>
<body>
  <style>
    .dataTables_wrapper { 
      padding: 4px;
      border: 1px solid black;
    }
    tr:hover {
      background-color: rgba(0, 0, 0, 0.1) !important;
    }
  </style>
  TABLE_HERE
  <script>
    $(document).ready(function (){
      $('table').DataTable({
        scrollX: true,
        scrollY: 480,
      });
    });
  </script>
</body>
</html>
"""

def grid_search_cv_to_html(results, dataset, model, strategy):
  grid_search_results_df = pd.DataFrame(results)
  results_name = f"{dataset['name']}_{model['name']}_{strategy}".lower()
  grid_search_results_df.to_csv(f"{DATASETS_FOLDER}/{results_name}.csv")

  grid_search_results_df_html = grid_search_results_df.to_html()
  html_string = BASE_HTML.replace('TABLE_HERE', grid_search_results_df_html)
  html_file = open(f"{RESULTS_FOLDER}/{results_name}.html", 'w')
  html_file.write(html_string)
  html_file.close()

def log(info):
  with open('log.txt', 'a') as log_file:
    print(info)
    log_file.write(f"{info}\n")

RESULTS_DATASET_PATH = f"{DATASETS_FOLDER}/results.csv"
def write_result_dataset(row):
    if os.path.isfile(RESULTS_DATASET_PATH):
      with open(RESULTS_DATASET_PATH, 'a') as results_dataset_file:
        results_dataset_file.write(f"{row}\n")
    else:
      with open(RESULTS_DATASET_PATH, 'a') as results_dataset_file:
        results_dataset_file.write("dataset,regressor,strategy,mse\n")
        results_dataset_file.write(f"{row}\n")

"""## Modelos"""

def many_to_many(dataset, model, X_train, X_test, y_train, y_test):
  grid_search_cv_name =  'multi_output_grid_search_cv'
  
  if model['support_multiple_output']:
    grid_search_cv_name = 'grid_search_cv'

  model[grid_search_cv_name].fit(X_train, y_train)

  best_model = model[grid_search_cv_name].best_estimator_

  mse = mean_squared_error(y_test, best_model.predict(X_test))

  grid_search_cv_to_html(
    model[grid_search_cv_name].cv_results_,
    dataset,
    model,
    'many_to_many',
  )

  log(f"MSE ({dataset['name']}) ({model['name']}) (*_mag --> *_err): {mse:.15f}")
  write_result_dataset(f"{dataset['name']},{model['name']},many_to_many,{mse:.15f}")

def many_to_one(dataset, model, X_train, X_test, y_train, y_test):
  mses = []
  for target_column in Y_TARGET_COLUMNS:
    y_train_one_target = y_train[target_column]
    y_test_one_target = y_test[target_column]

    model['grid_search_cv'].fit(X_train, y_train_one_target)

    best_model = model['grid_search_cv'].best_estimator_

    mse = mean_squared_error(y_test_one_target, best_model.predict(X_test))
    mses.append(mse)

    grid_search_cv_to_html(
      model['grid_search_cv'].cv_results_,
      dataset,
      model,
      f"many_to_one_{target_column}",
    )

    log(f"MSE ({dataset['name']}) ({model['name']}) (*_mag --> {target_column}): {mse:.15f}")
  log(f"MSE ({dataset['name']}) ({model['name']}) (*_mag --> ?_err): {mean(mses):.15f}")
  write_result_dataset(f"{dataset['name']},{model['name']},many_to_one,{mean(mses):.15f}")

def one_to_one(dataset, model, X_train, X_test, y_train, y_test):
  mses = []
  for (feature_column, target_column) in zip(X_FEATURE_COLUMNS, Y_TARGET_COLUMNS):
    X_train_one_feature = X_train[feature_column].to_numpy().reshape(-1, 1)
    X_test_one_feature = X_test[feature_column].to_numpy().reshape(-1, 1)

    y_train_one_target = y_train[target_column]
    y_test_one_target = y_test[target_column]

    model['grid_search_cv'].fit(X_train_one_feature, y_train_one_target)

    best_model = model['grid_search_cv'].best_estimator_

    mse = mean_squared_error(y_test_one_target, best_model.predict(X_test_one_feature))
    mses.append(mse)

    grid_search_cv_to_html(
      model['grid_search_cv'].cv_results_,
      dataset,
      model,
      f"one_to_one_{feature_column}_{target_column}",
    )

    log(f"MSE ({dataset['name']}) ({model['name']}) ({feature_column} --> {target_column}): {mse:.15f}")
  log(f"MSE ({dataset['name']}) ({model['name']}) (?_mag --> ?_err): {mean(mses):.15f}")
  write_result_dataset(f"{dataset['name']},{model['name']},one_to_one,{mean(mses):.15f}")

"""# Experimentos"""

time_start = perf_counter()

for dataset in DATASETS:
  X_train, X_test, y_train, y_test = load_split_dataset(dataset)

  for model in MODELS:
    many_to_many(dataset, model, X_train, X_test, y_train, y_test)
    many_to_one(dataset, model, X_train, X_test, y_train, y_test)
    one_to_one(dataset, model, X_train, X_test, y_train, y_test)

time_end = perf_counter()

log(f"Elapsed time: {time_end - time_start}s")

"""# Resultados"""

results_df = pd.read_csv("datasets/results.csv")
results_df.to_latex("results/results.tex")

results_df_html = results_df.to_html()
html_string = BASE_HTML.replace('TABLE_HERE', results_df_html)
html_file = open("results/results.html", 'w')
html_file.write(html_string)
html_file.close()