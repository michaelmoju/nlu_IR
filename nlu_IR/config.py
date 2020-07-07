import os
from pathlib import Path

SRC_ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
PROJ_ROOT = SRC_ROOT.parent

DATA_ROOT = PROJ_ROOT / "data"
RESULT_PATH = PROJ_ROOT / "results"
PREDICTION_PATH = PROJ_ROOT / "prediction"
DATABASE_ROOT = PROJ_ROOT / "database"

# Datasets
HOTPOT_TRAIN = DATA_ROOT / "hotpotqa" / "hotpot_train_v1.1.json"
HOTPOT_DEV = DATA_ROOT / "hotpotqa" / "hotpot_dev_fullwiki_v1.json"
HOTPOT_TEST = DATA_ROOT / "hotpotqa" / "hotpot_test_fullwiki_v1.json"

COS_TRAIN = DATA_ROOT / "cosQA" / "movieqa_1.2" / "movieqa_train.json"
COS_DEV = DATA_ROOT / "cosQA" / "movieqa_1.2" / "movieqa_dev.json"
COS_TEST = DATA_ROOT / "cosQA" / "movieqa_1.2" / "movieqa_test.json"

COS_WIKI = DATA_ROOT / "cosQA" / "doc"

DS_SSQA = DATA_ROOT / "SSQA" / "Elementary_Social_Studies_v2.9"

# Index directory
IDX_COS_ZH = DATABASE_ROOT / "IDX_cosZH"
IDX_COS_EN = DATABASE_ROOT / "IDX_cosEN"

# Whole: 5_486_211
# ABS: 5_233_329
HOTPOT_WIKI_ABS = DATA_ROOT / "hotpotqa" / "enwiki-20171001-pages-meta-current-withlinks-abstracts-test"
HOTPOT_WIKI_PRC = DATA_ROOT / "hotpotqa" / "enwiki-20171001-pages-meta-current-withlinks-processed"

# Databases
DB_HOTPOT_WIKI = DATABASE_ROOT / "hotpot_wiki.db"
DB_SSQA = DATABASE_ROOT / "ssqa.db"

# TRAINED_MODELS = RESULT_PATH / "trainedmodels"
# BERT_EMBEDDING = "bert-base-chinese"
# BERT_EMBEDDING_ZH = "bert-base-chinese"