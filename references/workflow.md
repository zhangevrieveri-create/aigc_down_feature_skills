# 完整流程

顺序不要打乱：先让数字正确，再动文字。文字改得再好，数字对不上就是废稿。

## 0. 收集
- 拿到：实证部分全文、所有表、图的说明、（有则）回测/程序的原始输出、目标期刊或参考范文。
- 问清楚：哪些结果来自训练期、哪些来自样本外；消融是"单独去除"还是"逐步叠加"；年化口径和起止日期；对比方法的定义。

## 1. 审计（数字自洽）
运行 `python scripts/audit_metrics.py spec.json` 回算 ICIR、卡玛、年化、提升百分比等。

## 2. 精简与补充建议
删样本内无意义个案，保留样本外主对比、消融与统计显著性。

## 3. 选风格
运行 `python scripts/select_style.py 原稿.txt`。

## 4. 改写
冻结数字，套用对应档案的 Native 学术句式。

## 5. 校验
- `python scripts/check_numbers.py 原文.txt 改写.txt --strip-refs`
- `python scripts/overlap_check.py 改写.txt --style <风格id>`