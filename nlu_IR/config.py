import os
from pathlib import Path

SRC_ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
PROJ_ROOT = SRC_ROOT.parent

DATA_ROOT = PROJ_ROOT / "data"
RESULT_PATH = PROJ_ROOT / "results"
PREDICTION_PATH = PROJ_ROOT / "prediction"
DATABASE_ROOT = PROJ_ROOT / "database"

HOTPOT_TRAIN = DATA_ROOT / "hotpotqa" / "hotpot_train_v1.1.json"
HOTPOT_DEV = DATA_ROOT / "hotpotqa" / "hotpot_dev_fullwiki_v1.json"
HOTPOT_TEST = DATA_ROOT / "hotpotqa" / "hotpot_test_fullwiki_v1.json"

# Whole: 5_486_211
# ABS: 5_233_329
HOTPOT_WIKI_ABS = DATA_ROOT / "hotpotqa" / "enwiki-20171001-pages-meta-current-withlinks-abstracts"
HOTPOT_WIKI_PRC = DATA_ROOT / "hotpotqa" / "enwiki-20171001-pages-meta-current-withlinks-processed"

#
HOTPOT_WIKI_DB = DATABASE_ROOT / "hotpot_wiki.db"

TRAINED_MODELS = RESULT_PATH / "trainedmodels"
BERT_EMBEDDING = "bert-base-chinese"
BERT_EMBEDDING_ZH = "bert-base-chinese"