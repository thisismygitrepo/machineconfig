

from typing import Literal


def generate_qrcode_grid(
    strings: list[str],
    output_path: str,
    per_row: int = 3,
    qr_size: int = 200,
    label_height: int = 30,
    padding: int = 20,
    label_max_chars: int = 25,
    format: Literal["svg", "png"] = "svg",
) -> str:
    from pathlib import Path
    if not strings:
        raise ValueError("strings list cannot be empty")

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    if format == "svg":
        return _generate_svg(strings, output_path, per_row, qr_size, label_height, padding, label_max_chars)
    elif format == "png":
        return _generate_png(strings, output_path, per_row, qr_size, label_height, padding, label_max_chars)
    else:
        raise ValueError(f"Unsupported format: {format}")


def _generate_svg(
    strings: list[str],
    output_path: str,
    per_row: int,
    qr_size: int,
    label_height: int,
    padding: int,
    label_max_chars: int,
) -> str:
    num_items = len(strings)
    num_rows = (num_items + per_row - 1) // per_row

    cell_width = qr_size
    cell_height = qr_size + label_height
    total_width = per_row * cell_width + (per_row + 1) * padding
    total_height = num_rows * cell_height + (num_rows + 1) * padding

    from xml.etree import ElementTree as ET

    import qrcode
    svg_root = ET.Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        width=str(total_width),
        height=str(total_height),
        viewBox=f"0 0 {total_width} {total_height}",
    )

    _bg_rect = ET.SubElement(svg_root, "rect", width=str(total_width), height=str(total_height), fill="white")

    for idx, text in enumerate(strings):
        row = idx // per_row
        col = idx % per_row

        x_offset = padding + col * (cell_width + padding)
        y_offset = padding + row * (cell_height + padding)

        qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_L, box_size=10, border=2, image_factory=qrcode.image.svg.SvgPathImage)  # type: ignore
        qr.add_data(text)
        qr.make(fit=True)

        qr_img = qr.make_image()
        qr_svg_string = qr_img.to_string(encoding="unicode")

        qr_tree = ET.fromstring(qr_svg_string)

        group = ET.SubElement(svg_root, "g", transform=f"translate({x_offset}, {y_offset})")

        qr_group = ET.SubElement(group, "g")
        for child in qr_tree:
            qr_group.append(child)

        label_text = text[:label_max_chars] if len(text) > label_max_chars else text
        text_y = qr_size + label_height // 2

        text_elem = ET.SubElement(
            group,
            "text",
            x=str(qr_size // 2),
            y=str(text_y),
            fill="black",
            attrib={
                "font-family": "monospace",
                "font-size": "12",
                "text-anchor": "middle",
                "dominant-baseline": "middle",
            },
        )
        text_elem.text = label_text

    tree = ET.ElementTree(svg_root)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="unicode", xml_declaration=True)

    return output_path


def _generate_png(
    strings: list[str],
    output_path: str,
    per_row: int,
    qr_size: int,
    label_height: int,
    padding: int,
    label_max_chars: int,
) -> str:
    num_items = len(strings)
    num_rows = (num_items + per_row - 1) // per_row

    cell_width = qr_size
    cell_height = qr_size + label_height
    total_width = per_row * cell_width + (per_row + 1) * padding
    total_height = num_rows * cell_height + (num_rows + 1) * padding

    import qrcode
    import qrcode.image.pil
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (total_width, total_height), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
    except OSError:
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except OSError:
            font = ImageFont.load_default()

    for idx, text in enumerate(strings):
        row = idx // per_row
        col = idx % per_row

        x_offset = padding + col * (cell_width + padding)
        y_offset = padding + row * (cell_height + padding)

        qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_L, box_size=10, border=2, image_factory=qrcode.image.pil.PilImage)
        qr.add_data(text)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

        img.paste(qr_img_resized, (x_offset, y_offset))

        label_text = text[:label_max_chars] if len(text) > label_max_chars else text

        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x_offset + (qr_size - text_width) // 2
        text_y = y_offset + qr_size + label_height // 2 - 6

        draw.text((text_x, text_y), label_text, fill="black", font=font)

    img.save(output_path, format="PNG")

    return output_path
