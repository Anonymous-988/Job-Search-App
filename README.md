# 🔍 Job Hunter Pro

A powerful, AI-driven job hunting application built with Streamlit that helps job seekers discover opportunities and company career pages across industries. Powered by SERP API for real-time job data and Azure OpenAI for intelligent filtering and validation.

![Job Hunter Pro](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

### 🎯 **Smart Job Search**
- **Real-time job discovery** using SERP API (Google Jobs)
- **AI-powered job filtering** with Azure OpenAI GPT models
- **Advanced filtering options**: Employment type, work mode, experience level
- **Location-based search** with remote work options
- **Intelligent job ranking** based on user preferences
- **Direct application links** to company job postings

### 🏢 **Industry Career Pages Discovery**
- **Automated career page discovery** across 15+ industry domains
- **Company size filtering**: MNCs vs Startups
- **AI validation** to ensure legitimate career pages
- **Duplicate removal** and quality scoring
- **Bulk export options** (CSV, URL lists)
- **Advanced search options** with location and keyword filtering

### 🤖 **AI-Powered Intelligence**
- **Azure OpenAI integration** for job relevance scoring
- **Career page validation** using LLM reasoning
- **Smart company name extraction** from URLs and titles
- **Automated duplicate detection** and removal
- **Transparent AI reasoning** with explanation of selection criteria

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- SERP API account ([serpapi.com](https://serpapi.com))
- Azure OpenAI service access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anonymous-988/Job-Search-App.git
   cd Job-Search-App
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   ```
   http://localhost:8501
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# SERP API Configuration
SERP_API_KEY="your_serp_api_key_here"

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
AZURE_OPENAI_API_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_API_DEPLOYMENT_NAME="gpt-35-turbo"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

### API Setup

#### 1. SERP API Setup
1. Sign up at [serpapi.com](https://serpapi.com)
2. Get your API key from the dashboard
3. Add to `.env` file as `SERP_API_KEY`

#### 2. Azure OpenAI Setup
1. Create an Azure OpenAI resource in Azure Portal
2. Deploy a GPT model (recommended: GPT-3.5 Turbo or GPT-4)
3. Get the following from your Azure resource:
   - **API Key**: From "Keys and Endpoint" section
   - **Endpoint**: Your resource endpoint URL
   - **Deployment Name**: Name of your deployed model
   - **API Version**: Use latest stable version

## 📋 Requirements

```txt
streamlit>=1.28.0
requests>=2.31.0
openai>=1.3.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

## 🎯 Usage

### Tab 1: Smart Job Search

1. **Enter job details**:
   - Position/Job Title (required)
   - Location (optional)
   - Employment Type (Full-time, Part-time, etc.)
   - Work Mode (Remote, On-site, Hybrid)
   - Experience Level

2. **Configure search**:
   - Set number of results (5-100)
   - Enable/disable AI filtering

3. **Search and review**:
   - AI filters most relevant jobs
   - View detailed job cards with direct apply links
   - Export results if needed

### Tab 2: Industry Career Pages Discovery

1. **Select criteria**:
   - Choose industry domain (15+ options)
   - Select company size (MNCs vs Startups)
   - Set number of companies to discover

2. **Advanced options** (optional):
   - Location focus
   - Exclude keywords (recruiters, agencies)
   - Enable/disable AI validation

3. **Discover and validate**:
   - System finds career pages via SERP API
   - AI validates legitimate company pages
   - View results in cards or table format
   - Export URLs or download CSV

## 🏗️ Architecture

### Core Components

```
Job-Search-App/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── .env.example          # Environment template
└── README.md             # This file
```

### Data Flow

1. **User Input** → Search criteria and filters
2. **SERP API** → Raw job/career page data
3. **Data Processing** → Clean and structure results
4. **Azure OpenAI** → Intelligent filtering and validation
5. **Display** → Formatted results with export options

### API Integration

- **SERP API**: Google Jobs and Google Search engines
- **Azure OpenAI**: GPT-3.5/4 models for content analysis
- **Rate Limiting**: Built-in delays to respect API quotas
- **Error Handling**: Graceful degradation when APIs unavailable

## 🎨 Customization

### Adding New Industries

Edit the `industry_domains` list in `app.py`:

```python
self.industry_domains = [
    "Your New Industry",
    "Another Industry",
    # ... existing industries
]
```

### Modifying Search Parameters

Customize search strategies in the `discover_career_pages_by_industry` method:

```python
industry_keywords = {
    "Your Industry": "your keywords OR alternative terms",
    # ... other industries
}
```

### UI Customization

Modify the CSS in the `st.markdown` sections to change styling:

```python
st.markdown("""
<style>
    .your-custom-class {
        /* Your custom styles */
    }
</style>
""", unsafe_allow_html=True)
```

## 📊 Supported Industries

- 🚀 Technology & Software
- 💰 Financial Services & Fintech
- 🏥 Healthcare & Biotechnology
- 🛒 E-commerce & Retail
- 📊 Consulting & Professional Services
- 🏭 Manufacturing & Automotive
- 🎬 Media & Entertainment
- ⚡ Energy & Utilities
- 🏘️ Real Estate & Construction
- 📚 Education & EdTech
- 🍔 Food & Beverage
- 🚛 Transportation & Logistics
- 📡 Telecommunications
- 🎮 Gaming & Digital Entertainment
- ✈️ Aerospace & Defense

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Errors
```bash
# Check .env file exists and has correct keys
ls -la .env
cat .env
```

#### 2. No Results Found
- Verify SERP API key is valid and has credits
- Try broader search terms
- Check if industry keywords match your target

#### 3. Azure OpenAI Errors
- Ensure deployment name matches exactly
- Verify API version compatibility
- Check quota limits in Azure portal

#### 4. Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run app.py --logger.level debug
```

### Environment Variables Not Loading

Ensure `python-dotenv` is installed and `.env` file is in project root:

```bash
pip install python-dotenv
ls -la .env
```

## 📈 Performance Tips

1. **API Rate Limits**:
   - Use smaller batch sizes for initial testing
   - Enable AI filtering only when needed
   - Monitor API usage in dashboards

2. **Search Optimization**:
   - Use specific industry terms
   - Combine location filters for targeted results
   - Exclude common non-company keywords

3. **Memory Usage**:
   - Limit result counts for large searches
   - Clear Streamlit cache periodically
   - Use table view for better performance with many results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [SERP API](https://serpapi.com/) for real-time search data
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) for AI capabilities
- [OpenAI](https://openai.com/) for the underlying language models

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Anonymous-988/Job-Search-App/issues)
- **Email**: sumant.m.pujari@gmail.com

## 🔄 Version History

- **v1.0.0** - Initial release with job search and career page discovery
- **v1.1.0** - Added Azure OpenAI integration and AI filtering
- **v1.2.0** - Enhanced industry domains and startup filtering
- **v1.3.0** - Added export options and advanced search parameters

---

<div align="center">

**⭐ Star this repository if you found it helpful! ⭐**

Made with ❤️ by [Sumant Pujari](https://github.com/Anonymous-988)

</div>