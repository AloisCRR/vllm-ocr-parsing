# VLLM OCR Parsing

A Python project that uses vision language models (VLLM) to extract structured data from restaurant menu PDFs and images through OCR processing.

## Features

- **PDF Processing**: Convert PDF pages to images for OCR analysis
- **Vision Language Model Integration**: Uses OpenRouter API with Qwen3-VL model for intelligent text extraction
- **Structured Data Extraction**: Extracts detailed menu items with categories, prices, ingredients, dietary tags, and more
- **Data Pipeline**: Built with dlt for reliable data processing and storage
- **Database Storage**: Stores results in DuckDB for easy querying and analysis
- **Interactive Interface**: Marimo-based web interface for easy operation

## Installation

### Prerequisites

- Python 3.13+
- OpenRouter API key
- Poppler (for PDF processing)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd vllm-ocr-parsing
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Install Poppler (required for pdf2image):
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from http://blog.alivate.com.au/poppler-windows/ and add to PATH
```

4. Set up environment variables:
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

## Usage

### Interactive Mode

Run the Marimo application for an interactive web interface:

```bash
uvx "marimo[recommended]" edit --no-token -p 2718 --sandbox --watch vllm_ocr.py
```

This will open a web interface where you can:
- Select PDF files for processing
- Run the OCR pipeline with a click
- Monitor processing progress

## Data Schema

The system extracts structured menu data with the following fields:

- **name**: Item name
- **description**: Detailed description
- **price**: Item price
- **category**: Main category (Appetizers, Main Course, etc.)
- **subCategory**: Sub-category within main category
- **ingredients**: List of identifiable ingredients
- **dietaryTags**: Dietary flags (vegetarian, vegan, keto, etc.)
- **spicinessLevel**: 0-5 scale for spiciness
- **portionSize**: Portion context (2 units, 8 pieces, 300g, etc.)
- **tags**: General tags for the item

## API Details

### OpenRouter Integration

- **Model**: Qwen3-VL-30B-A3B-Instruct
- **Endpoint**: https://openrouter.ai/api/v1/chat/completions
- **Response Format**: Structured JSON schema for consistent output

### Data Pipeline

The system uses dlt (Data Load Tool) for:
- Reliable data processing with error handling
- Automatic schema inference
- DuckDB integration for storage
- Incremental loading capabilities

## Output

Processed data is stored in a DuckDB database (`restaurant_menu_ocr.duckdb`) with:
- Raw OCR responses
- Structured menu data
- Processing metadata
- Error handling information

## Dependencies

- `pdf2image`: PDF to image conversion
- `pillow`: Image processing
- `pypdf2`: PDF manipulation
- `python-dotenv`: Environment variable management
- `requests`: HTTP client for API calls
- `dlt`: Data pipeline framework
- `marimo`: Interactive notebook interface
- `duckdb`: Database storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Poppler not found**: Ensure Poppler is installed and in your PATH
2. **API key errors**: Verify OPENROUTER_API_KEY is set correctly
3. **PDF processing errors**: Check that PDF files are not password-protected
4. **Memory issues**: Large PDFs may require additional RAM

### Getting Help

- Check the OpenRouter API documentation for model availability and usage
- Review the dlt documentation for pipeline configuration options
- Ensure all dependencies are properly installed with correct versions