# Installation Guide

YamlQL can be installed using pip, the Python package installer. It requires Python 3.9 or later.

## Requirements

- Python 3.9+
- pip or uv package manager
- For AI features:
  - OpenAI API key (for OpenAI provider)
  - Google API key (for Gemini provider)

## Installation Methods

### Using pip

```bash
pip install yamlql
```

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer. To install YamlQL using uv:

```bash
uv pip install yamlql
```

### Development Installation

To install YamlQL for development:

```bash
# Clone the repository
git clone https://github.com/AKSarav/YamlQL.git
cd YamlQL

# Install in development mode
pip install -e .
```

## Verifying Installation

After installation, verify that YamlQL is working correctly:

```bash
yamlql --version
```

You should see the current version number of YamlQL.

## Setting Up AI Features

YamlQL supports multiple LLM providers for natural language querying. You'll need to set up the appropriate environment variables for your chosen provider.

### OpenAI Setup

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Set environment variables:
   ```bash
   export YAMLQL_LLM_PROVIDER="OpenAI"
   export OPENAI_API_KEY="your-api-key"
   ```

### Google Gemini Setup

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variables:
   ```bash
   export YAMLQL_LLM_PROVIDER="Gemini"
   export GEMINI_API_KEY="your-api-key"
   ```

### Using .env File

You can also create a `.env` file in your project directory:

```ini
YAMLQL_LLM_PROVIDER=OpenAI
OPENAI_API_KEY=your-api-key
# or
# YAMLQL_LLM_PROVIDER=Gemini
# GEMINI_API_KEY=your-api-key
```

## Troubleshooting

### Common Issues

1. **Python Version Error**
   ```
   ERROR: YamlQL requires Python 3.9 or later
   ```
   Solution: Upgrade your Python installation or use a virtual environment with Python 3.9+.

2. **Missing Dependencies**
   ```
   ERROR: No module named 'duckdb'
   ```
   Solution: Try reinstalling with `pip install --no-cache-dir yamlql`

3. **LLM Provider Issues**
   ```
   ERROR: YAMLQL_LLM_PROVIDER environment variable not set
   ```
   Solution: Set the environment variable as shown in the AI setup section.

### Getting Help

If you encounter any issues:

1. Check the [Troubleshooting Guide](../troubleshooting.md)
2. Search for similar issues on [GitHub](https://github.com/AKSarav/YamlQL/issues)
3. Open a new issue if your problem isn't already reported 