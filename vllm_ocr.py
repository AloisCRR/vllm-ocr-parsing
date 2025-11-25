# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "dlt[duckdb]==1.18.2",
#     "openai==2.8.1",
#     "pdf2image==1.17.0",
#     "requests==2.32.5",
# ]
# ///

import marimo

__generated_with = "0.18.0"
app = marimo.App(width="columns", app_title="VLLM Restaurant Menu OCR")


@app.cell
def _():
    import marimo as mo
    import requests
    import json
    import base64
    import os
    import dlt
    from typing import Dict, Any
    from pathlib import Path
    from pdf2image import convert_from_path
    from pdf2image import pdfinfo_from_path
    return (
        Any,
        Dict,
        Path,
        base64,
        convert_from_path,
        dlt,
        json,
        mo,
        os,
        pdfinfo_from_path,
        requests,
    )


@app.cell
def _(Path, base64):
    def encode_image_to_base64(image_path: str) -> str:
        """Encode image file to base64 data URL."""
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Determine image type from file extension
        ext = Path(image_path).suffix.lower()
        if ext == ".png":
            mime_type = "image/png"
        elif ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".webp":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"  # default

        return f"data:{mime_type};base64,{base64_image}"


    def encode_pil_image_to_base64(image, mime_type: str = "image/jpeg") -> str:
        """Encode PIL Image object to base64 data URL in memory."""
        import io

        # Convert PIL Image to bytes in memory
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        buffer.close()

        # Encode to base64
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        return f"data:{mime_type};base64,{base64_image}"
    return (encode_pil_image_to_base64,)


@app.cell
def _(convert_from_path):
    def extract_pdf_page_to_image(pdf_path: str, page_num: int):
        """Extract specific page from PDF and return PIL Image object."""
        if convert_from_path is None:
            raise ImportError("pdf2image is required for PDF processing")

        # Convert PDF page to image (page_num is 1-based)
        images = convert_from_path(
            pdf_path, first_page=page_num, last_page=page_num
        )

        if not images:
            raise ValueError(f"Could not extract page {page_num} from PDF")

        # Return the first (and only) image as PIL Image object
        return images[0]
    return (extract_pdf_page_to_image,)


@app.cell
def _(Any, Dict):
    def get_menu_item_schema() -> Dict[str, Any]:
        """Get JSON schema for MenuItem structured output."""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "menu_items",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "menuItems": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the menu item",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Detailed description of the menu item",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "Price of the item",
                                    },
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "General tags for the item",
                                    },
                                    "category": {
                                        "type": "string",
                                        "description": "Main category (e.g., Appetizers, Main Course, etc.)",
                                    },
                                    "subCategory": {
                                        "type": "string",
                                        "description": "Sub-category within the main category",
                                    },
                                    "ingredients": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of ingredients in the item",
                                    },
                                    "dietaryTags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Dietary flags",
                                    },
                                    "spicinessLevel": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 5,
                                        "description": "Spiciness level from 0 (bland) to 5 (very spicy)",
                                    },
                                    "portionSize": {
                                        "type": "string",
                                        "description": "Portion context (e.g., 2 units, 8 pieces, 300g)",
                                    },
                                },
                                "required": [
                                    "name",
                                    "description",
                                    "price",
                                    "tags",
                                    "category",
                                    "spicinessLevel",
                                    "ingredients",
                                    "dietaryTags",
                                ],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["menuItems"],
                    "additionalProperties": False,
                },
            },
        }
    return (get_menu_item_schema,)


@app.cell
def _(Any, Dict, get_menu_item_schema, requests):
    def parse_menu_with_openrouter(
        base64_image: str, api_key: str
    ) -> Dict[str, Any]:
        """Parse menu image using OpenRouter API with structured output."""

        # Prepare API request
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "qwen/qwen3-vl-30b-a3b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Extract all menu items from this restaurant menu image. For each item, provide:
    - Item name and description
    - Price
    - Category and sub-category
    - All ingredients you can identify
    - Dietary tags (vegetarian, vegan, keto, gluten-friendly-option, etc.)
    - Spiciness level (0-5 scale, if applicable)
    - Portion size information
    - General tags

    Be thorough and accurate. If information is not visible for a field, make reasonable inferences based on the item name and description. Maintain the language of the image in your results.""",
                        },
                        {"type": "image_url", "image_url": {"url": base64_image}},
                    ],
                }
            ],
            "provider": {
                "require_parameters": True,
            },
            "response_format": get_menu_item_schema(),
        }

        # Make API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()
    return (parse_menu_with_openrouter,)


@app.cell
def _(
    dlt,
    encode_pil_image_to_base64,
    extract_pdf_page_to_image,
    json,
    os,
    parse_menu_with_openrouter,
    pdfinfo_from_path,
):
    @dlt.resource(write_disposition="replace")
    def process_pdf_pages(pdf_path: str, api_key: str):
        """Process all pages of a PDF and yield OCR responses with metadata."""

        try:
            info = pdfinfo_from_path(pdf_path)
            total_pages = info["Pages"]
        except Exception as e:
            raise ValueError(f"Could not get PDF info: {e}")

        for page_num in range(1, total_pages + 1):
            try:
                print(f"Processing page {page_num}/{total_pages}...")

                # Extract page as PIL Image
                image = extract_pdf_page_to_image(pdf_path, page_num)

                # Convert to base64
                base64_image = encode_pil_image_to_base64(image)

                # Parse with OpenRouter
                ocr_response = parse_menu_with_openrouter(base64_image, api_key)

                # Extract menu data from response
                choices = ocr_response.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    menu_data = json.loads(content)

                    # Yield structured data with metadata
                    yield {
                        "pdf_path": pdf_path,
                        "page_number": page_num,
                        "total_pages": total_pages,
                        "ocr_response": ocr_response,
                        "menu_data": menu_data,
                        "menu_items": menu_data.get("menuItems", []),
                        "item_count": len(menu_data.get("menuItems", [])),
                        "processed_at": json.dumps(
                            {"timestamp": str(os.times())}
                        ),  # Simple timestamp
                    }
                else:
                    # Yield error case
                    yield {
                        "pdf_path": pdf_path,
                        "page_number": page_num,
                        "total_pages": total_pages,
                        "ocr_response": ocr_response,
                        "menu_data": None,
                        "menu_items": [],
                        "item_count": 0,
                        "error": "No valid response from OpenRouter",
                        "processed_at": json.dumps({"timestamp": str(os.times())}),
                    }

            except Exception as e:
                # Yield error case for this page
                yield {
                    "pdf_path": pdf_path,
                    "page_number": page_num,
                    "total_pages": total_pages,
                    "ocr_response": None,
                    "menu_data": None,
                    "menu_items": [],
                    "item_count": 0,
                    "error": str(e),
                    "processed_at": json.dumps({"timestamp": str(os.times())}),
                }
    return (process_pdf_pages,)


@app.cell
def _(mo):
    pdf_file = mo.ui.file_browser(
        selection_mode="file",
        multiple=False,
        filetypes=[".pdf"],
        label="Select the PDF to OCR",
    )

    pdf_file
    return (pdf_file,)


@app.cell
def _(pdf_file):
    # Get the selected PDF path
    selected_pdf = pdf_file.path(index=0) if pdf_file.value else None

    selected_pdf
    return (selected_pdf,)


@app.cell
def _(mo):
    run_ingest_pipeline = mo.ui.run_button(label="Click to run the OCR pipeline")

    run_ingest_pipeline
    return (run_ingest_pipeline,)


@app.cell
def _(
    dlt,
    mo,
    os,
    pdf_file,
    process_pdf_pages,
    run_ingest_pipeline,
    selected_pdf,
):
    mo.stop(not run_ingest_pipeline.value, mo.md("Click the button to run"))

    """Main function to process PDF with dlt pipeline and store in DuckDB."""
    # Check if a PDF is selected
    if not selected_pdf:
        raise ValueError("No PDF file selected. Please select a PDF file first.")

    # Configuration
    _pdf_path = str(selected_pdf)
    _api_key = os.getenv("OPENROUTER_API_KEY")

    if not _api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Please set this environment variable to continue."
        )

    try:
        # Create dlt pipeline with DuckDB destination
        pipeline = dlt.pipeline(
            pipeline_name="restaurant_menu_ocr",
            destination="duckdb",
            dataset_name="mandu",  # This becomes the schema name
        )

        print(f"Processing PDF: {_pdf_path}")
        print("Starting OCR pipeline...")

        # Run the pipeline
        load_info = pipeline.run(
            process_pdf_pages(_pdf_path, _api_key),
            table_name=pdf_file.name(index=0),
        )

        print("Pipeline completed successfully!")
        print(f"Load info: {load_info}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    return


if __name__ == "__main__":
    app.run()
