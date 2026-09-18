# long-pdf-reader —— 长篇 PDF 可靠阅读技能

把"读不完、读不准、读过就忘"的长 PDF / 扫描书籍变成**可恢复的外部证据记忆**：分批建立页级笔记，跨会话断点续读，所有回答都锚定到源页码。

## 解决什么问题

书籍级 PDF 哪怕勉强塞进大上下文，也会遇到：检索稀释、OCR 噪声、页码引用丢失、后文覆盖前文、压缩/新会话后无法恢复、重复通读成本高昂。本技能用**页级可寻址的外部记忆**替代"把整本书粘进对话"。

## 核心机制

- **六层记忆**：L0 原始 PDF（不可变）→ L1 抽取/OCR → L2 页块笔记 → L3 章节综合 → L4 全书地图 → L5 会话状态（断点指针）
- **双页码体系**：PDF 页索引与印刷页码分开记录，引用永不混淆
- **证据分级**：作者陈述 / 直接证据 / 模型推断 三者严格区分；公式、表格、图形必须回看渲染页核实，OCR 只作检索辅助
- **覆盖率账本**：每页状态（pending/surveyed/indexed/excluded/audited）精确记录，没处理完就不宣称"读完全书"
- **断点续读**：每批次写 checkpoint，新会话读 manifest + session_state 即可继续，不必重读已完成页面

## 使用方式

```bash
# 初始化阅读工作区
python scripts/book_workspace.py init \
  --root <workspace> --title <书名> --source <pdf路径> --pages <PDF页数>

# 声明索引进度前强制校验
python scripts/book_workspace.py validate --root <workspace>
```

脚本仅依赖 Python 标准库，不解析、不修改 PDF 本体。

## 工作区产物

```
book_manifest.json   # 源文件身份 + SHA-256
page_map.csv         # PDF页 ↔ 印刷页码 ↔ 标题路径
coverage.csv         # 逐页处理状态账本
book_map.md          # 全书导航地图
evidence_ledger.md   # 证据台账
session_state.md     # 断点续读指针
notes/chunks/        # 页块笔记（不可变，含中英检索词）
notes/chapters/      # 章节综合（由块笔记派生）
```

## 适用场景

- 中英双语、含公式/表格/图形的教材、规范、专著
- 扫描版书籍（OCR 噪声、双页扫描、旋转页面）
- 需要跨多个会话反复查询的长文档
- 需要"第 X 页原文怎么说"级别的可核查回答

普通短 PDF 直接读即可，无需本技能。

## WorkBuddy/Windows 适配说明

本仓库版本在原版基础上做了两处适配（原版面向 POSIX + OpenAI 生态）：

1. frontmatter 描述追加中文触发词，提升中文语境下的技能自动匹配率
2. SKILL.md 新增 Runtime adaptation 小节，命令示例改用托管 Python 解释器路径（Windows 下无 `python3` 命令），并建议工作区放在项目目录内以便跨会话恢复

## 文件结构

```
SKILL.md                          # 技能主文档（工作流 + 质量门禁）
scripts/book_workspace.py         # 工作区初始化/校验（纯标准库）
references/extraction-and-ocr.md  # 扫描件分级处理、OCR 验收标准
references/memory-and-retrieval.md# 六层记忆模型与检索策略
references/schemas.md             # 全部产物的数据模板
```

## 许可

按原始技能包用途自由使用与修改。
