# -*- coding: utf-8 -*-
"""ratio_check.py —— 检查 HTML 正文中指定区块（如推广区）的字数占比。

用法:
    python ratio_check.py body.html --start "推广区起始标记" \\
        --end "推广区结束标记" --threshold 30

退出码: 占比 <= 阈值为 0，超过为 1（可接入 CI）。
"""
import argparse
import re
import sys


def plain_text_len(html):
    """去标签后的纯文字长度。"""
    return len(re.sub(r"<[^>]+>", "", html))


def main():
    ap = argparse.ArgumentParser(description="HTML 指定区块字数占比检查")
    ap.add_argument("html", help="正文 HTML 文件")
    ap.add_argument("--start", required=True, help="区块起始标记（纯文本）")
    ap.add_argument("--end", required=True, help="区块结束标记（纯文本）")
    ap.add_argument("--threshold", type=float, default=30,
                    help="占比百分比上限，默认 30")
    args = ap.parse_args()

    with open(args.html, "r", encoding="utf-8") as f:
        body = f.read()

    s = body.find(args.start)
    e = body.find(args.end)
    if s == -1 or e == -1:
        sys.exit(f"未找到标记: start={s != -1}, end={e != -1}")
    e = body.find("</p>", e)
    if e == -1:
        e = len(body)

    section_len = plain_text_len(body[s:e])
    total_len = plain_text_len(body)
    ratio = section_len / total_len * 100 if total_len else 0
    ok = ratio <= args.threshold
    print(f"区块: {section_len} 字 / 全文: {total_len} 字 "
          f"= {ratio:.1f}% {'[OK]' if ok else '[OVER]'} 上限 {args.threshold}%")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
