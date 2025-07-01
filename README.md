# tg2kb

Telegram to Knowledge Base - Convert Telegram channel dumps into structured Markdown-based knowledge bases.

## 🎯 Project Purpose

`tg2kb` is a CLI tool that transforms Telegram channel exports into organized, searchable knowledge bases. It processes each message as an atomic note, extracting titles, generating summaries, and creating tagged Markdown files.

## 🚀 Features

- **Multi-format Support**: Load Telegram dumps in JSON, TXT, or HTML formats
- **Smart Processing**: Extract titles, generate summaries, and auto-tag content using LLM
- **Structured Output**: Create linked Markdown notes with metadata
- **Cross-references**: Generate index files with tags and note relationships
- **Direct Integration**: Fetch messages directly from Telegram using Telethon
- **Modular Pipeline**: Run individual steps or the complete workflow

## 📁 Project Structure

```
tg2kb/
├── cli.py                # Main CLI entrypoint
├── parser.py             # Telegram dump parser
├── processor.py          # Content processor (LLM integration)
├── generator.py          # Markdown generator
├── tg_client.py          # Telethon client for direct Telegram access
├── security_check.py     # Security validation and credential checks
├── run_parser.py         # Standalone parser runner
├── run_processor.py      # Standalone processor runner
├── run_generator.py      # Standalone generator runner
├── examples/
│   ├── sample_dump.json  # Sample Telegram export
│   └── raw_dump.json     # Downloaded messages (generated)
├── outputs/
│   └── notes/            # Generated knowledge base
├── requirements.txt      # Python dependencies
├── config.example.env    # Example environment file
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd tg2kb
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Telegram API** (for direct access):
   - Visit https://my.telegram.org
   - Create an application to get `api_id` and `api_hash`

4. **Configure credentials**:
   ```bash
   cp config.example.env .env
   # Edit .env with your actual credentials
   ```

## 🔐 Security

### Credential Management
- **Never commit credentials** to version control
- Use `.env` files for local development
- Set environment variables for production
- Run `python security_check.py` to validate security

### Security Checks
The project includes automatic security validation:

```bash
# Run security checks manually
python security_check.py

# Pre-commit hooks automatically run security checks
git commit -m "Your message"  # Will block if issues found
```

### What's Protected
- ✅ Hardcoded API keys in code
- ✅ Session files (.session)
- ✅ Environment files (.env)
- ✅ Credential patterns in files
- ✅ Required environment variables

## 📖 Usage

### Full Pipeline
```bash
# Convert a Telegram dump to knowledge base
python cli.py convert examples/sample_dump.json --output ./kb

# Use different input format
python cli.py convert dump.txt --format txt --output ./kb

# Skip index generation
python cli.py convert dump.json --no-index
```

### Individual Steps
```bash
# Parse only
python cli.py parse dump.json --output parsed.json

# Process only
python cli.py process parsed.json --output processed.json

# Generate only
python cli.py generate processed.json --output ./kb
```

### Direct Telegram Access
```bash
# Download messages directly from Telegram
python tg_client.py
```

### Standalone Scripts
```bash
# Run individual pipeline steps
python run_parser.py
python run_processor.py
python run_generator.py
```

## 🔧 Configuration

### Environment Variables
- `TELEGRAM_API_ID`: Your Telegram API ID from https://my.telegram.org
- `TELEGRAM_API_HASH`: Your Telegram API Hash from https://my.telegram.org
- `OPENAI_API_KEY`: Your OpenAI API key for LLM processing
- `TELEGRAM_SESSION_NAME`: Custom session name (optional, default: tg2kb_session)

### Output Structure
The generated knowledge base includes:
- **Individual Markdown notes** for each message
- **index.json** with tags and cross-references
- **Metadata** embedded in each note
- **Tag-based organization**

## 🧪 Development

This is a scaffold project ready for hackathon development. Each module contains:
- Comprehensive TODO comments
- Function stubs with proper type hints
- Clear separation of concerns
- Error handling placeholders

### Key Modules to Implement:
1. **`parser.py`**: Load and parse Telegram exports
2. **`processor.py`**: LLM-based content processing
3. **`generator.py`**: Markdown and index generation
4. **`tg_client.py`**: Direct Telegram access

### Security Best Practices
- Always run security checks before committing
- Use environment variables, never hardcode credentials
- Keep `.env` files local and never commit them
- Use the provided security validation tools

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here] 