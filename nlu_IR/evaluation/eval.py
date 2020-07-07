def eval_sp(golds, predictions):
    metrics = {'sp_em': 0, 'sp_prec': 0, 'sp_recall': 0, 'sp_f1': 0}
    
    assert len(golds) == len(predictions)
    
    for gold, pred in zip(golds, predictions):
        _update_sp(metrics, gold, pred)
        
    N = len(golds)
    for k in metrics.keys():
        metrics[k] /= N
        metrics[k] = round(metrics[k], 3)
    print(metrics)
    return metrics


def _update_sp(metrics, gold, pred):
    tp, fp, fn = 0, 0, 0
        
    for p in pred:
        if p in gold:
            tp += 1
        else:
            fp += 1
    for g in gold:
        if g not in pred:
            fn += 1
    precision = 1.0 * tp / (tp + fp) if tp + fp > 0 else 0.0
    if len(gold) == 0:
        recall = 1.0
    else:
        recall = 1.0 * tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    em = 1.0 if fp + fn == 0 else 0.0
    metrics['sp_em'] += em
    metrics['sp_f1'] += f1
    metrics['sp_prec'] += precision
    metrics['sp_recall'] += recall
    
    return precision, recall, f1