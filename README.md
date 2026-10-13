# edu-content-kb-template

面向内容团队的「事实—产品—内容—规范」四库知识库模板，附一套从资料提取到图文发布的通用脚本。

不含任何真实业务数据：所有品牌、账号、领域均为 `{{占位符}}`，原始资料目录默认不入库。适合作为内部知识库或个人内容工作流的起点。

## 目录结构

```
.
├── README.md
├── templates/
│   ├── 00_知识库索引模板.md      # 四库结构 + 入库规则 + 台账
│   ├── 01_入库登记表模板.md      # 可信度分级、信源顺序、使用规则
│   └── 02_内容排版自检清单模板.md # 平台兼容规范 + 合规自检
├── scripts/
│   ├── xlsx_dump.py             # 纯标准库读取 xlsx，导出 CSV（免装 pandas）
│   ├── html_inject.py           # 正文 HTML 注入预览模板的 JSON 数据块
│   ├── ratio_check.py           # 指定区块字数占比检查（如推广区 ≤30%）
│   ├── ocr_pdf.py               # 扫描版 PDF 批量 OCR（pypdfium2 + tesseract）
│   └── svg_to_png.ps1           # Edge/Chrome 无头模式 SVG 转 PNG
└── data/                        # 本地资料目录（.gitignore 排除，不入库）
```

## 搭建步骤

### 1. 初始化自己的知识库

复制模板文件（不带脚本也可以单独用）：

```powershell
Copy-Item templates\00_知识库索引模板.md 你的知识库\索引.md
Copy-Item templates\01_入库登记表模板.md 你的知识库\
Copy-Item templates\02_内容排版自检清单模板.md 你的知识库\
```

全局替换占位符：`{{账号名}}`、`{{品牌名}}`、`{{领域}}`、`{{主色色值}}` 等。

### 2. 建立四库

| 库 | 放什么 | 典型来源 |
|----|--------|----------|
| A 事实库 | 客观事实：政策、行业数据、公开报告、时间节点 | 官方渠道公开文件、权威媒体 |
| B 产品库 | 自有产品资料、「用户问题 ↔ 产品」映射 | 产品手册、培训资料（**内部资料不外传**） |
| C 内容库 | 已发布内容存档、选题池、复盘 | 自己的平台账号 |
| D 规范库 | 人设、语气、排版、禁用词、免责模板 | 团队约定 |

每份资料进库时在登记表登记一行，关键规则：

- 易过期数字标 `⚠️待核实`，按官方信源顺序复核。
- 内部资料标注「对外引用需过滤」，定价、名单、未公开计划不原样对外。
- OCR/机器提取文本的关键数字必须人工回查。

### 3. 工具链用法

所有脚本均为命令行参数驱动，不包含任何硬编码路径。

```bash
# 查看 xlsx 全部 sheet
python scripts/xlsx_dump.py data/某数据表.xlsx --outdir data/csv_out

# 只看某个 sheet
python scripts/xlsx_dump.py data/某数据表.xlsx --sheet "Sheet1"

# 正文注入预览模板
python scripts/html_inject.py --template preview.html --body body.html \
  --title "标题" --date "2026-01-01"

# 推广区占比检查（超过 30% 退出码为 1，可接 CI）
python scripts/ratio_check.py body.html \
  --start "推广区起始句" --end "推广区结束句" --threshold 30

# 扫描版 PDF 批量 OCR
python scripts/ocr_pdf.py data/扫描件.pdf data/ocr_out --start 0 --end 20

# SVG 转 PNG（Windows，自动查找 Edge/Chrome）
powershell -ExecutionPolicy Bypass -File scripts/svg_to_png.ps1 \
  -SvgPath chart.svg -PngPath chart.png -Width 640 -Height 480
```

依赖：

```bash
pip install pypdfium2 pillow   # OCR 脚本需要；xlsx 解析与 HTML 工具仅用标准库
# tesseract 需另行安装并配置中文语言包，路径可用 --tesseract 或 TESSERACT_BIN 指定
```

### 4. 单篇内容生产流程建议

1. 选题 → 在 A 库查事实，在 B 库找衔接点，在 C 库查是否重复。
2. 写正文 HTML（扁平结构 + 行内样式，规范见自检清单）。
3. 数据可视化用 SVG 制作，发布前转 PNG。
4. `html_inject.py` 注入预览模板 → 浏览器自检。
5. `ratio_check.py` 卡推广占比 → 对照自检清单做合规检查。
6. 粘贴到平台后台 → 手机预览 → 发布 → 回写 C 库台账与复盘。

## 合规与安全红线

- **原始资料不入库**：`data/` 已被 gitignore。内部 PDF/Excel、含定价或名单的文件永远不要提交到任何远程仓库。
- **公开发布前全局搜索**：品牌内部代号、真实人名、定价、本机用户名、未公开数据。
- **工具不替你判断内容合规**：广告披露、免责声明、效果承诺限定等以平台规则和当地法规为准。
- 建议用 [gitleaks](https://github.com/gitleaks/gitleaks) 在提交前扫描密钥类信息。

## 许可

本模板（脚本与文档结构）可按团队需要自由使用、修改和分发；使用本模板构建的知识库内容版权归各自所有者。
