

import typer
from typing import Annotated, Optional


def merge_pdfs(
        pdfs: Annotated[list[str], typer.Argument(..., help="Paths to the PDF files to merge.")],
        output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output merged PDF file path.")] = None,
        compress: Annotated[bool, typer.Option("--compress", "-c", help="Compress the output PDF.")] = False,
    ) -> None:
    def merge_pdfs_internal(pdfs: list[str], output: str | None, compress: bool) -> None:
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter()
        for pdf_path in pdfs:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        output_path = output if output else "merged.pdf"
        if compress:
            try:
                for p in writer.pages:
                    try:
                        # PageObject.compress_content_streams exists in pypdf
                        p.compress_content_streams()
                    except Exception:
                        # best-effort: ignore per-page compression failures
                        continue
            except Exception:
                pass
            try:
                writer.compress_identical_objects()
            except Exception:
                # non-fatal if this fails
                pass
        writer.write(output_path)
        print(f"✅ Merged PDF saved to: {output_path}")
    from machineconfig.utils.meta import lambda_to_python_script
    code = lambda_to_python_script(lambda : merge_pdfs_internal(pdfs=pdfs, output=output, compress=compress),
                                   in_global=True, import_module=False)
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script
    uv_command, _py_file = get_uv_command_executing_python_script(python_script=code, uv_with=["pypdf"], uv_project_dir=None)
    run_shell_script(uv_command)


def compress_pdf(
        pdf_input: Annotated[str, typer.Argument(..., help="Path to the input PDF file to compress.")],
        output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output compressed PDF file path.")] = None,
        quality: Annotated[int, typer.Option("--quality", "-q", help="JPEG quality for image compression (0-100, 0=no change, 100=best).")] = 85,
        image_dpi: Annotated[int, typer.Option("--image-dpi", "-d", help="Target DPI for image resampling. If set, images above this DPI will be downsampled.")] = 0,
        # remove_images: Annotated[bool, typer.Option("--remove-images", "-r", help="Remove all images from the PDF.")] = False,
        compress_streams: Annotated[bool, typer.Option("--compress-streams", "-c", help="Compress uncompressed streams.")] = True,
        use_objstms: Annotated[bool, typer.Option("--object-streams", "-s", help="Use object streams for additional compression.")] = True,
    ) -> None:
    def compress_pdf_internal(pdf_input: str, output: str | None, quality: int, image_dpi: int, compress_streams: bool, use_objstms: bool) -> None:
        import pymupdf
        from pathlib import Path
        output_path = output if output else pdf_input.replace(".pdf", "_compressed.pdf")
        doc = pymupdf.open(pdf_input)
        try:
            # if remove_images:
            #     for page in doc:
            #         page.remove_images()
            if quality > 0 or image_dpi > 0:
                doc.rewrite_images(
                    dpi_threshold=image_dpi if image_dpi > 0 else None,
                    dpi_target=max(72, image_dpi - 10) if image_dpi > 72 else 72,
                    quality=quality,
                    lossy=True,
                    lossless=True,
                )
            doc.save(
                output_path,
                deflate=compress_streams,
                garbage=3,
                use_objstms=1 if use_objstms else 0,
            )
            input_size = Path(pdf_input).stat().st_size
            output_size = Path(output_path).stat().st_size
            ratio = (1 - output_size / input_size) * 100
            print(f"✅ Compressed PDF saved to: {output_path}")
            print(f"   Original: {input_size / 1024 / 1024:.2f} MB")
            print(f"   Compressed: {output_size / 1024 / 1024:.2f} MB")
            print(f"   Reduction: {ratio:.1f}%")
        finally:
            doc.close()
    from machineconfig.utils.meta import lambda_to_python_script
    code = lambda_to_python_script(
        lambda: compress_pdf_internal(pdf_input=pdf_input, output=output, quality=quality, image_dpi=image_dpi, compress_streams=compress_streams, use_objstms=use_objstms),
        in_global=True,
        import_module=False,
    )
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script
    uv_command, _py_file = get_uv_command_executing_python_script(python_script=code, uv_with=["pymupdf"], uv_project_dir=None)
    run_shell_script(uv_command)

