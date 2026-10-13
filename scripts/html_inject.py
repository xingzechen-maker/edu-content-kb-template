# -*- coding: utf-8 -*-
"""html_inject.py —— 把正文 HTML 注入预览模板的 JSON 数据块。

预览模板中需包含:
    <script id="post-data" type="application/json">
    {"title":"","date":"","body_html":""}
    </script>

本脚本用标准库 json 完成转义，避免手工字符串替换导致 JSON 损坏。

用法:
    python html_inject.py --template preview.html --body body.html \\
        --title "标题" --date "2026-01-01" --output preview.html
"""
import argparse
import json
import re
import sys

PATTERN = re.compile(
    r'(<script id="post-data" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)


def inject(template_text, body_html, title, date):
    match = PATTERN.search(template_text)
    if not match:
        sys.exit("模板中未找到 <script id=\"post-data\" ...> JSON 块")
    data = json.loads(match.group(2).strip())
    data["title"] = title
    data["date"] = date
    data["body_html"] = body_html
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    return (template_text[:match.start(2)]
            + "\n" + new_json + "\n"
            + template_text[match.end(2):])


def main():
    ap = argparse.ArgumentParser(description="正文 HTML 注入预览模板")
    ap.add_argument("--template", required=True, help="预览模板 HTML 路径")
    ap.add_argument("--body", required=True, help="正文 HTML 片段路径")
    ap.add_argument("--title", default="", help="文章标题")
    ap.add_argument("--date", default="", help="发布日期文本")
    ap.add_argument("--output", help="输出路径（默认覆盖 template）")
    args = ap.parse_args()

    with open(args.template, "r", encoding="utf-8") as f:
        template = f.read()
    with open(args.body, "r", encoding="utf-8") as f:
        body = f.read()

    result = inject(template, body, args.title, args.date)
    out = args.output or args.template
    with open(out, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"[OK] 已注入: {out}")
    checks = {
        "标题": args.title in result if args.title else True,
        "正文": "body_html" in result and len(body) > 0,
    }
    for k, ok in checks.items():
        print(f"  {'[OK]' if ok else '[FAIL]'} {k}")


if __name__ == "__main__":
    main()
