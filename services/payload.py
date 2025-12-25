from .aggregators import ratio, type_ratio, weekly_usage


def build_stats_payload(apps):
    weekly_labels, weekly_values = weekly_usage(apps)
    ratio_labels, ratio_values, ratio_total = ratio(apps)
    type_labels, type_values, type_total = type_ratio(apps)
    # Chart.js が期待するキー構造の JSON ペイロードを返す。
    # `ratio_total`/`type_total` は UI 上の合計表示と一致させるためにも使う。
    return {
        'weekly_labels': weekly_labels,
        'weekly_values': weekly_values,
        'ratio_labels': ratio_labels,
        'ratio_values': ratio_values,
        'ratio_total': ratio_total,
        'type_labels': type_labels,
        'type_values': type_values,
        'type_total': type_total,
    }
