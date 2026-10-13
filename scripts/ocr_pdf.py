# -*- coding: utf-8 -*-
"""ocr_pdf.py —— 扫描版 PDF 批量 OCR（渲染页面 + tesseract 命令行）。

依赖:
    pip install pypdfium2 pillow
    另需安装 tesseract 及中文语言包 chi_sim

用法:
    python ocr_pdf.py input.pdf output_dir --start 0 --end -1
    python ocr_pdf.py input.pdf output_dir --tesseract "C:/tools/tesseract/tesseract.exe"

环境变量（命令行参数优先级更高）:
    TESSERACT_BIN   tesseract 可执行文件路径
    TESSDATA_PREFIX tessdata 目录路径
"""
import argparse
import io
import os
import subprocess
import sys

def ocr_page(pdf, idx, tesseract, lang, psm, scale):
    page = pdf[idx]
    bitmap = page.render(scale=scale)
    img = bitmap.to_pil()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    cmd = [tesseract, "stdin", "stdout", "-l", lang, "--psm", str(psm)]
    proc = subprocess.run(cmd, input=buf.getvalue(),
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          timeout=180)
    return proc.stdout.decode("utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description="扫描版 PDF 批量 OCR")
    ap.add_argument("pdf", help="输入 PDF 路径")
    ap.add_argument("outdir", help="输出目录（每页一个 page_NNNN.txt）")
    ap.add_argument("--start", type=int, default=0, help="起始页（0 基，默认 0）")
    ap.add_argument("--end", type=int, default=-1, help="结束页（-1 表示末页）")
    ap.add_argument("--scale", type=float, default=2.5, help="渲染缩放，默认 2.5")
    ap.add_argument("--lang", default="chi_sim", help="tesseract 语言，默认 chi_sim")
    ap.add_argument("--psm", default="3", help="tesseract 页面分割模式，默认 3")
    ap.add_argument("--tesseract",
                    default=os.environ.get("TESSERACT_BIN", "tesseract"),
                    help="tesseract 路径，默认取 PATH 或环境变量 TESSERACT_BIN")
    args = ap.parse_args()

    if not os.path.isfile(args.pdf):
        sys.exit(f"PDF 不存在: {args.pdf}")
    os.makedirs(args.outdir, exist_ok=True)

    try:
        import pypdfium2 as pdfium
    except ImportError:
        sys.exit("缺少依赖，请先安装: pip install pypdfium2 pillow")

    pdf = pdfium.PdfDocument(args.pdf)
    total = len(pdf)
    end = total if args.end < 0 else min(args.end, total)
    print(f"total_pages={total} range={args.start}-{end}")

    for i in range(args.start, end):
        out = os.path.join(args.outdir, f"page_{i + 1:04d}.txt")
        if os.path.exists(out):
            print(f"skip page {i + 1} (exists)")
            continue
        try:
            text = ocr_page(pdf, i, args.tesseract, args.lang, args.psm, args.scale)
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[OK] page {i + 1}, {len(text)} chars")
        except Exception as e:
            with open(out, "w", encoding="utf-8") as f:
                f.write(f"[OCR_ERROR] {e}\n")
            print(f"[ERR] page {i + 1}: {e}")


if __name__ == "__main__":
    main()
