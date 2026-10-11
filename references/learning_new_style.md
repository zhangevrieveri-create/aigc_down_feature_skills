# 学习新风格（"后门"）与自动选风格

## 先说清楚这是什么
这里的"学习"是把样本文章归纳成一份风格档案（量化指标 + 写法模式），之后改写时按档案执行。不是微调模型。
- 档案存在 styles/<id>/ 里；文章原文默认不保存，只保存统计特征和哈希指纹（用于查重）。
- 样本版权归原作者；只用于归纳模式，不得照搬句子。

## 步骤
1. 收集样本：同一类期刊、同一类章节（如"实证结果"），至少5篇，最好来自不同作者；越多越稳。
2. 运行：
   python scripts/ingest_corpus.py --id <新id> --name "<名称>" --keywords "<领域关键词,逗号分隔>" 样本1.pdf 样本2.txt ...
   生成 features.json、fingerprints.json、profile.md 骨架，并登记到 _registry.json。
3. 阅读样本（抽取各篇的结果与讨论部分），按 styles/_template/profile.md 的 8 个小节写出模式。
4. 试改写一段文字，跑 check_numbers.py 与 overlap_check.py --style <id>。