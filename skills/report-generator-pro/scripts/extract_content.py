#!/usr/bin/env python3
"""
extract_content.py - 从多种文件格式抽取工作内容
支持: docx, xlsx, csv, pdf, txt, md
"""
import argparse
import sys
import os
import json

def extract_docx(file_path):
    try:
        from docx import Document
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except ImportError:
        return f"[错误] 需要安装 python-docx: pip install python-docx"
    except Exception as e:
        return f"[错误] 读取 docx 失败: {e}"

def extract_xlsx(file_path):
    try:
        import pandas as pd
        # 读取所有 sheet
        xl = pd.ExcelFile(file_path)
        result = []
        for sheet in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            result.append(f"=== Sheet: {sheet} ===")
            result.append(df.to_string(index=False))
        return "\n".join(result)
    except ImportError:
        return f"[错误] 需要安装 pandas 和 openpyxl: pip install pandas openpyxl"
    except Exception as e:
        return f"[错误] 读取 xlsx 失败: {e}"

def extract_csv(file_path):
    try:
        import pandas as pd
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        return df.to_string(index=False)
    except Exception as e:
        try:
            import pandas as pd
            df = pd.read_csv(file_path, encoding='gbk')
            return df.to_string(index=False)
        except Exception as e2:
            return f"[错误] 读取 csv 失败: {e2}"

def extract_pdf(file_path):
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- 第{i+1}页 ---\n{text}")
        return "\n".join(text_parts)
    except ImportError:
        return f"[错误] 需要安装 pdfplumber: pip install pdfplumber"
    except Exception as e:
        return f"[错误] 读取 pdf 失败: {e}"

def extract_txt(file_path):
    for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return "[错误] 无法解码文件，请确认文件编码"

def main():
    parser = argparse.ArgumentParser(description='从文件抽取工作内容')
    parser.add_argument('--file', required=True, help='文件路径')
    parser.add_argument('--type', help='文件类型（可选，自动检测）')
    parser.add_argument('--output', help='输出 JSON 路径（可选）')
    args = parser.parse_args()

    file_path = args.file
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"文件不存在: {file_path}"}, ensure_ascii=False))
        sys.exit(1)

    ext = args.type or os.path.splitext(file_path)[1].lower().lstrip('.')

    extractors = {
        'docx': extract_docx,
        'doc': extract_docx,
        'xlsx': extract_xlsx,
        'xls': extract_xlsx,
        'csv': extract_csv,
        'pdf': extract_pdf,
        'txt': extract_txt,
        'md': extract_txt,
    }

    extractor = extractors.get(ext)
    if not extractor:
        result = {"error": f"不支持的文件格式: .{ext}，支持格式: {list(extractors.keys())}"}
    else:
        content = extractor(file_path)
        result = {
            "success": True,
            "file": os.path.basename(file_path),
            "type": ext,
            "content": content,
            "char_count": len(content)
        }

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"已保存到: {args.output}")
    else:
        print(output_json)

if __name__ == '__main__':
    main()
