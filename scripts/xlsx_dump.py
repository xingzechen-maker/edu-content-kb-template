# -*- coding: utf-8 -*-
"""xlsx_dump.py —— 纯标准库读取 .xlsx，逐 sheet 导出为 CSV。

不依赖 openpyxl / pandas，适合受限环境快速查看表格内容。

用法:
    python xlsx_dump.py <input.xlsx> [--outdir <dir>] [--sheet <名称>]

不传 --outdir 时输出到标准输出；指定后每个 sheet 写一个 CSV 文件。
"""
import argparse
import csv
import io
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def load_shared_strings(zf):
    """读取共享字符串表；文件不存在时返回空表。"""
    shared = []
    try:
        with zf.open("xl/sharedStrings.xml") as f:
            tree = ET.parse(f)
    except KeyError:
        return shared
    for si in tree.findall(".//s:si", NS):
        texts = si.findall(".//s:t", NS)
        shared.append("".join(t.text or "" for t in texts))
    return shared


def list_sheets(zf):
    """返回 [(sheet名, worksheet目标路径), ...]。"""
    with zf.open("xl/workbook.xml") as f:
        tree = ET.parse(f)
    sheets = [
        (s.get("name"),
         s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"))
        for s in tree.findall(".//s:sheet", NS)
    ]
    with zf.open("xl/_rels/workbook.xml.rels") as f:
        rel_tree = ET.parse(f)
    rels = {r.get("Id"): r.get("Target")
            for r in rel_tree.findall(f".//{REL_NS}Relationship")}
    result = []
    for name, rid in sheets:
        target = rels[rid]
        if not target.startswith("/"):
            target = "xl/" + target
        result.append((name, target.lstrip("/")))
    return result


def read_sheet(zf, target, shared):
    """读取单个 worksheet，返回二维列表（含表头行）。"""
    with zf.open(target) as f:
        tree = ET.parse(f)
    rows = []
    for row in tree.findall(".//s:row", NS):
        row_data = []
        for c in row.findall("s:c", NS):
            v = c.find("s:v", NS)
            val = v.text if v is not None else ""
            if c.get("t") == "s" and val:
                try:
                    val = shared[int(val)]
                except (ValueError, IndexError):
                    pass
            row_data.append(val)
        rows.append(row_data)
    return rows


def main():
    ap = argparse.ArgumentParser(description="纯标准库 xlsx -> CSV 导出工具")
    ap.add_argument("xlsx", help="输入 .xlsx 文件路径")
    ap.add_argument("--outdir", help="输出目录（不指定则打印到 stdout）")
    ap.add_argument("--sheet", help="只导出指定名称的 sheet")
    args = ap.parse_args()

    if not os.path.isfile(args.xlsx):
        sys.exit(f"文件不存在: {args.xlsx}")

    with zipfile.ZipFile(args.xlsx) as zf:
        shared = load_shared_strings(zf)
        sheets = list_sheets(zf)
        for name, target in sheets:
            if args.sheet and name != args.sheet:
                continue
            rows = read_sheet(zf, target, shared)
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerows(rows)
            csv_text = buf.getvalue()
            if args.outdir:
                os.makedirs(args.outdir, exist_ok=True)
                safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)
                out = os.path.join(args.outdir, f"{safe}.csv")
                with open(out, "w", encoding="utf-8-sig", newline="") as f:
                    f.write(csv_text)
                print(f"[OK] {name} -> {out} ({len(rows)} 行)")
            else:
                print(f"===== {name} =====")
                print(csv_text)


if __name__ == "__main__":
    main()
