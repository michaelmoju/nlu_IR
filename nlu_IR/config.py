import os
from pathlib import Path

SRC_ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
PROJ_ROOT = SRC_ROOT.parent

DATA_ROOT = PROJ_ROOT / "data"
RESULT_PATH = PROJ_ROOT / "results"
PREDICTION_PATH = PROJ_ROOT / "prediction"

FGC_DEV = DATA_ROOT / "FGC" / "FGC_release_1.7.13" / "FGC_release_all_dev.json"
FGC_TRAIN = DATA_ROOT / "FGC" / "FGC_release_1.7.13" / "FGC_release_all_train.json"
FGC_TEST = DATA_ROOT / "FGC" / "FGC_release_1.7.13" / "FGC_release_all_test.json"

HOTPOT_DEV = DATA_ROOT / "hotpot_dataset" / "FGC_hotpot_dev_distractor_v1(cn_refn).json"
HOTPOT_TRAIN = DATA_ROOT / "hotpot_dataset" / "FGC_hotpot_train_v1.1(cn).json"

TRAINED_MODELS = RESULT_PATH / "trainedmodels" 
# TRAINED_MODEL_PATH = TRAINED_MODELS / ""
# BERT_EMBEDDING = DATA_ROOT / "bert_chinese_total"
BERT_EMBEDDING = "bert-base-chinese"
BERT_EMBEDDING_ZH = "bert-base-chinese"