#!/usr/bin/env python3
"""Package existing local images into an offline teaching card. No pixel edits."""
import argparse
import base64
import json
from pathlib import Path

MIME_TYPES = {".png": "image/png", ".jpg": "image/jpeg",
              ".jpeg": "image/jpeg", ".webp": "image/webp"}
DEFAULT_INPUT = '{"title":"向外扩散的圆环","reference":null,"layer":null,"texture":null,"analysis":null}'

def image_data(path):
    if path is None:
        return None
    source = Path(path).resolve()
    mime = MIME_TYPES.get(source.suffix.lower())
    if mime is None:
        raise ValueError("图片仅支持 PNG、JPG 或 WebP")
    data = source.read_bytes()
    if not data:
        raise ValueError("图片文件为空")
    if mime == "image/png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("PNG 文件头不正确")
    if mime == "image/jpeg" and not data.startswith(b"\xff\xd8"):
        raise ValueError("JPG 文件头不正确")
    if mime == "image/webp" and not (
        data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    ):
        raise ValueError("WebP 文件头不正确")
    return {"data_url": "data:" + mime + ";base64," +
            base64.b64encode(data).decode("ascii")}

def read_analysis(path):
    if path is None:
        return None
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("summary"), str):
        raise ValueError("分析文件需要 summary 文字")
    schemas = {
        "rows": (("item", "method", "role"), 4),
        "changes": (("goal", "where", "result"), 3),
        "uses": (("direction", "role", "change"), 3),
    }
    for key, (fields, limit) in schemas.items():
        rows = value.get(key)
        if not isinstance(rows, list) or not 1 <= len(rows) <= limit:
            raise ValueError(f"{key} 需要 1 到 {limit} 行")
        for row in rows:
            if not isinstance(row, dict) or any(
                not isinstance(row.get(field), str) for field in fields
            ):
                raise ValueError(f"{key} 中每行需要文字字段：{', '.join(fields)}")
    return value

def build(title, reference, layer, texture, output, analysis=None):
    output_path = Path(output).resolve()
    if output_path.suffix.lower() != ".html":
        raise ValueError("输出文件必须使用 .html 后缀")
    for source in (reference, layer, texture):
        if source and Path(source).resolve() == output_path:
            raise ValueError("输出文件不能覆盖原图")
    payload = {"title": title, "reference": image_data(reference),
               "layer": image_data(layer), "texture": image_data(texture),
               "analysis": read_analysis(analysis)}
    # Prevent supplied titles from closing the JSON script element.
    serialized = json.dumps(payload, ensure_ascii=False).replace(
        "&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    template_path = Path(__file__).resolve().parent.parent / "assets/layer-card.html"
    template = template_path.read_text(encoding="utf-8")
    marker = '<script id="card-input" type="application/json">' + DEFAULT_INPUT + "</script>"
    if template.count(marker) != 1:
        raise ValueError("图卡模板中的数据入口缺失或重复")
    content = template.replace(
        marker, '<script id="card-input" type="application/json">' +
        serialized + "</script>", 1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="把已有图片放进离线单层特效图卡，不改原图。")
    parser.add_argument("--title", default="向外扩散的圆环")
    parser.add_argument("--reference", help="整体参考图，可省略")
    parser.add_argument("--layer", help="已有的独立单层截图，可省略")
    parser.add_argument("--texture", help="实际贴图，可省略")
    parser.add_argument("--analysis", help="本层的简短分析 JSON，可省略")
    parser.add_argument("--out", required=True, help="输出 HTML 路径")
    args = parser.parse_args()
    try:
        target = build(args.title, args.reference, args.layer, args.texture, args.out, args.analysis)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print("图卡已保存：" + str(target))

if __name__ == "__main__":
    main()
