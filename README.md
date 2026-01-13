# 📚 Smart PDF Translator

A powerful web-based PDF translator that uses AI vision models to translate books and documents from one language to another. Built with Streamlit and powered by OpenRouter AI models.

## ✨ Features

- 📤 **Easy PDF Upload** - Drag and drop interface
- 🌍 **Multiple Languages** - Support for Gujarati, Hindi, English, Marathi, Tamil, Telugu, Bengali, Punjabi, and more
- 🤖 **Multiple AI Models** - Choose from GPT-4o, Claude 3.5, Gemini, and free models
- 📄 **Flexible Page Selection** - Translate single pages, ranges, or entire books
- ⏱️ **Rate Limit Control** - Adjustable wait times to avoid API quota errors
- 💾 **Easy Download** - Get translations in TXT or Markdown format
- 📊 **Progress Tracking** - Real-time progress bar and status updates
- 🔄 **Auto Retry** - Automatic retry logic for failed requests

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ansh23-BI/Smart_pdf_translator.git
cd Smart_pdf_translator
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up your API key**

Create a `.env` file in the project root:
```
OPEN_ROUTER_KEY=your_api_key_here
```

Or enter it directly in the app's sidebar when running.

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Enter API Key** - Add your OpenRouter API key in the sidebar
2. **Select Model** - Choose an AI model (GPT-4o recommended)
3. **Choose Languages** - Select source and target languages or let the LLM detect the language.
4. **Upload PDF** - Drag and drop your PDF file
5. **Select Pages** - Choose which pages to translate
6. **Adjust Wait Time** - Set delay between pages (15s recommended for free models)
7. **Start Translation** - Click the button and wait for completion
8. **Download** - Save your translation as TXT or Markdown
9. **PDF Converter** - Convert the output to pdf
10. **Download the PDF** - Once converted you will see a download button to download the same.
11. **Restart Translation** - Restart the translation based on the requirement.

## 🤖 Supported Models

### Paid Models (Require Credits)
- **GPT-4o** - Best quality, ~$0.50-1.00 per 245 pages
- **Claude 3.5 Sonnet** - Excellent quality, ~$4-5 per 245 pages
- **GPT-4 Turbo** - Good quality, ~$2-3 per 245 pages
- **Gemini Flash 1.5** - Fast and cheap

### Free Models (Rate Limited)
- **Gemini 2.0 Flash** - Good quality, requires longer wait times
- **Gemini Flash 1.5** - Decent quality

## 🌍 Supported Languages

- Gujarati
- Hindi
- French
- English
- Marathi
- Tamil
- Telugu
- Bengali
- Punjabi
- Custom (enter any language)

## 💰 Cost Estimates

For a 245-page book:
- **GPT-4o**: ~$0.50 - $1.00
- **Claude 3.5 Sonnet**: ~$4.00 - $5.00
- **Free Models**: $0 (but slower with rate limits)

## ⚙️ Configuration

### Wait Time Settings
- **Free models**: 15-30 seconds recommended
- **Paid models**: 5-10 seconds recommended

### Batch Processing
For large books, translate in batches:
- Pages 1-30
- Pages 31-60
- And so on...

## 🛠️ Troubleshooting

### Rate Limit Errors (429)
- Increase wait time in sidebar
- Use paid models instead of free ones
- Add credits to your OpenRouter account

### Model Not Found (404)
- Check if the model is available on OpenRouter
- Try a different model from the dropdown

### Translation Quality Issues
- Use GPT-4o or Claude 3.5 Sonnet for best results
- Ensure you selected the correct source language

## 📁 Project Structure

```
Smart_pdf_translator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this, not in repo)
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenRouter](https://openrouter.ai/)
- Uses [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing

## 📧 Contact

Your Name - Anshul Sethiya
Collab: 

Project Link: (https://github.com/Ansh23-BI/Smart_pdf_translator)

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Note**: This tool requires an OpenRouter API key and credits for paid models. Free models are available but may have rate limits.
