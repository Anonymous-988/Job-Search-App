import streamlit as st
import requests
import json
from openai import AzureOpenAI
import pandas as pd
from typing import List, Dict, Any
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

# Configure page
st.set_page_config(
    page_title="Job Hunter Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .job-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .company-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fff;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class JobHunterApp:
    def __init__(self):
        self.setup_api_keys()
        self.setup_constants()
    
    def setup_api_keys(self):
        """Setup API keys and Azure OpenAI configuration in sidebar"""
        # with st.sidebar:
        #     st.header("🔑 API Configuration")
            
        #     # SERP API
        #     self.serp_api_key = st.text_input("SERP API Key", type="password", 
        #                                     help="Get your API key from serpapi.com")
            
        #     st.subheader("🤖 Azure OpenAI Configuration")
        #     self.azure_openai_api_key = st.text_input("Azure OpenAI API Key", type="password",
        #                                              help="Your Azure OpenAI API key")
        #     self.azure_openai_endpoint = st.text_input("Azure OpenAI Endpoint",
        #                                               placeholder="https://your-resource.openai.azure.com/",
        #                                               help="Your Azure OpenAI endpoint URL")
        #     self.azure_openai_deployment = st.text_input("Deployment Name",
        #                                                 placeholder="gpt-35-turbo or gpt-4",
        #                                                 value="gpt-35-turbo",
        #                                                 help="Your deployed model name in Azure OpenAI")
        #     self.azure_openai_api_version = st.selectbox("API Version",
        #                                                 ["2024-02-15-preview", "2023-12-01-preview", "2023-05-15"],
        #                                                 index=0,
        #                                                 help="Azure OpenAI API version")


        # SERP API
        self.serp_api_key = os.getenv("SERP_API_KEY")
        
        # Azure OpenAI API
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
        self.azure_openai_deployment = os.getenv("AZURE_API_DEPLOYMENT_NAME")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        # Initialize Azure OpenAI client
        self.azure_client = None
        if all([self.azure_openai_api_key, self.azure_openai_endpoint, self.azure_openai_deployment]):
            try:
                self.azure_client = AzureOpenAI(
                    api_key=self.azure_openai_api_key,
                    api_version=self.azure_openai_api_version,
                    azure_endpoint=self.azure_openai_endpoint
                )
                st.success("✅ Azure OpenAI configured successfully!")
            except Exception as e:
                st.error(f"❌ Azure OpenAI configuration error: {str(e)}")
        elif any([self.azure_openai_api_key, self.azure_openai_endpoint, self.azure_openai_deployment]):
            st.warning("⚠️ Please fill in all Azure OpenAI fields")
    
    def setup_constants(self):
        """Setup company lists and job search parameters"""
        self.employment_types = [
            "Full-time", "Part-time", "Contract", "Internship", "Temporary"
        ]
        
        self.work_modes = [
            "Remote", "On-site", "Hybrid"
        ]
        
        self.experience_levels = [
            "Entry Level", "Mid Level", "Senior Level", "Executive"
        ]
        
        # Industry domains for career page discovery
        self.industry_domains = [
            "Technology & Software",
            "Financial Services & Fintech",
            "Healthcare & Biotechnology",
            "E-commerce & Retail",
            "Consulting & Professional Services",
            "Manufacturing & Automotive",
            "Media & Entertainment",
            "Energy & Utilities",
            "Real Estate & Construction",
            "Education & EdTech",
            "Food & Beverage",
            "Transportation & Logistics",
            "Telecommunications",
            "Gaming & Digital Entertainment",
            "Aerospace & Defense"
        ]
        
        # Company size categories
        self.company_sizes = ["MNCs (Large Corporations)", "Startups (Small to Medium)"]
    
    def search_serp_jobs(self, query: str, location: str = "", num_results: int = 20) -> List[Dict]:
        """Search for jobs using SERP API"""
        if not self.serp_api_key:
            st.error("Please provide SERP API key")
            return []
        
        try:
            params = {
                "engine": "google_jobs",
                "q": query,
                "location": location,
                "api_key": self.serp_api_key,
                "num": min(num_results, 100)  # SERP API limit
            }
            
            response = requests.get("https://serpapi.com/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs_results", [])
                
                # Clean and structure job data
                cleaned_jobs = []
                for job in jobs:
                    cleaned_job = {
                        "title": job.get("title", ""),
                        "company": job.get("company_name", ""),
                        "location": job.get("location", ""),
                        "description": job.get("description", ""),
                        "via": job.get("via", ""),
                        "link": job.get("link", ""),
                        "thumbnail": job.get("thumbnail", ""),
                        "posted_at": job.get("detected_extensions", {}).get("posted_at", ""),
                        "schedule_type": job.get("detected_extensions", {}).get("schedule_type", ""),
                        "work_from_home": job.get("detected_extensions", {}).get("work_from_home", False)
                    }
                    cleaned_jobs.append(cleaned_job)
                
                return cleaned_jobs
            else:
                st.error(f"SERP API Error: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error searching jobs: {str(e)}")
            return []
    
    def discover_career_pages_by_industry(self, industry: str, company_size: str, num_results: int = 50) -> List[Dict]:
        """Discover career pages by industry and company size using SERP API"""
        if not self.serp_api_key:
            st.error("Please provide SERP API key")
            return []
        
        try:
            # Build search query based on industry and company size
            size_keywords = {
                "MNCs (Large Corporations)": "Fortune 500 OR multinational OR corporation OR enterprise OR global company",
                "Startups (Small to Medium)": "startup OR tech startup OR emerging company OR scale-up OR growing company"
            }
            
            industry_keywords = {
                "Technology & Software": "software company OR tech company OR IT company",
                "Financial Services & Fintech": "bank OR financial services OR fintech OR investment",
                "Healthcare & Biotechnology": "healthcare company OR biotech OR pharmaceutical OR medical",
                "E-commerce & Retail": "ecommerce OR retail company OR online marketplace",
                "Consulting & Professional Services": "consulting firm OR professional services OR advisory",
                "Manufacturing & Automotive": "manufacturing company OR automotive OR industrial",
                "Media & Entertainment": "media company OR entertainment OR broadcasting OR streaming",
                "Energy & Utilities": "energy company OR utilities OR renewable energy OR oil gas",
                "Real Estate & Construction": "real estate OR construction company OR property development",
                "Education & EdTech": "education company OR edtech OR learning platform OR university",
                "Food & Beverage": "food company OR beverage OR restaurant chain OR food tech",
                "Transportation & Logistics": "logistics company OR transportation OR supply chain OR shipping",
                "Telecommunications": "telecom company OR telecommunications OR wireless OR network",
                "Gaming & Digital Entertainment": "gaming company OR game developer OR digital entertainment",
                "Aerospace & Defense": "aerospace company OR defense contractor OR aviation"
            }
            
            # Construct search query
            base_query = f"({industry_keywords.get(industry, industry)}) AND ({size_keywords.get(company_size, '')}) careers site:careers OR site:jobs"
            
            params = {
                "engine": "google",
                "q": base_query,
                "api_key": self.serp_api_key,
                "num": min(num_results, 100),
                "gl": "us",
                "hl": "en"
            }
            
            st.info(f"🔍 Searching: {base_query}")
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic_results", [])
                
                st.info(f"📊 Found {len(organic_results)} raw results from SERP API")
                
                # Process and clean results
                career_pages = []
                for result in organic_results:
                    link = result.get("link", "")
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    
                    # Extract company name from title or domain
                    company_name = self.extract_company_name(title, link)
                    
                    # Basic filtering for career-related pages
                    career_keywords = ["career", "job", "hiring", "work", "employment", "talent", "opportunity", "join"]
                    
                    if any(keyword in link.lower() or keyword in title.lower() for keyword in career_keywords):
                        career_page = {
                            "company_name": company_name,
                            "title": title,
                            "career_url": link,
                            "description": snippet,
                            "domain": self.extract_domain(link),
                            "industry": industry,
                            "company_size": company_size
                        }
                        career_pages.append(career_page)
                
                return career_pages
            
            else:
                st.error(f"SERP API Error: {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            st.error(f"Error discovering career pages: {str(e)}")
            return []
    
    def extract_company_name(self, title: str, url: str) -> str:
        """Extract company name from title or URL"""
        # Try to extract from title first
        if " - " in title:
            potential_company = title.split(" - ")[0].strip()
            if len(potential_company) < 50 and not any(word in potential_company.lower() for word in ["career", "job", "hiring"]):
                return potential_company
        
        # Extract from domain
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove common prefixes and suffixes
            domain = domain.replace("www.", "").replace("careers.", "").replace("jobs.", "")
            
            if "." in domain:
                company_part = domain.split(".")[0]
                return company_part.replace("-", " ").title()
            
            return domain.title()
        except:
            return "Unknown Company"
    
    def extract_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace("www.", "")
        except:
            return url
    
    def filter_career_pages_with_llm(self, career_pages: List[Dict], criteria: Dict) -> List[Dict]:
        """Use Azure OpenAI to filter and validate career pages based on criteria"""
        if not self.azure_client or not career_pages:
            if not self.azure_client:
                st.warning("Azure OpenAI not configured. Returning unfiltered results.")
            return career_pages
        
        try:
            # Prepare career pages data for LLM
            pages_summary = []
            for i, page in enumerate(career_pages[:100], 1):  # Limit for token efficiency
                summary = f"""
                Company {i}:
                Name: {page['company_name']}
                Domain: {page['domain']}
                Title: {page['title']}
                Description: {page['description'][:300]}
                Industry: {page['industry']}
                Size Category: {page['company_size']}
                URL: {page['career_url']}
                """
                pages_summary.append(summary)
            
            # Create LLM prompt for filtering
            prompt = f"""
            You are an expert at evaluating company career pages. Please analyze these career page results and select only the most legitimate and relevant ones based on the following criteria:

            FILTERING CRITERIA:
            - Industry: {criteria.get('industry', 'Any')}
            - Company Size: {criteria.get('company_size', 'Any')}
            - Maximum Results Needed: {criteria.get('num_results', 20)}

            VALIDATION REQUIREMENTS:
            1. Must be actual company career pages (not job boards, recruiters, or aggregators)
            2. Company name should be clearly identifiable and legitimate
            3. Domain should belong to the actual company
            4. Should match the requested industry and company size category
            5. Remove duplicates (same company with different URLs)
            6. Prioritize well-known, established companies

            COMPANIES TO ANALYZE:
            {chr(10).join(pages_summary[:50])}

            Please return a JSON array with company numbers (1-based) that meet the criteria, ordered by relevance and company reputation.
            Format: {{"selected_companies": [1, 3, 5, 7, ...], "reasoning": "Brief explanation of selection criteria applied"}}
            Only return valid JSON, no additional text.
            """

            # Make Azure OpenAI API call
            response = self.azure_client.chat.completions.create(
                model=self.azure_openai_deployment,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional HR and business analyst expert at identifying legitimate company career pages. Always respond with valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse LLM response
            try:
                # Clean the response
                if result.startswith("```json"):
                    result = result[7:-3]
                elif result.startswith("```"):
                    result = result[3:-3]
                
                parsed_result = json.loads(result)
                selected_indices = parsed_result.get("selected_companies", [])
                reasoning = parsed_result.get("reasoning", "AI filtering applied")
                
                # Convert 1-based indices to 0-based and filter pages
                filtered_pages = []
                for idx in selected_indices:
                    if 1 <= idx <= len(career_pages):
                        filtered_pages.append(career_pages[idx-1])
                
                if filtered_pages:
                    st.success(f"🤖 AI validated {len(filtered_pages)} legitimate career pages from {len(career_pages)} candidates")
                    st.info(f"💡 AI Reasoning: {reasoning}")
                    return filtered_pages[:criteria.get('num_results', 20)]
                else:
                    st.warning("AI filtering returned no valid results, showing top unfiltered results")
                    return career_pages[:criteria.get('num_results', 20)]
                
            except json.JSONDecodeError as e:
                st.warning(f"AI response parsing failed: {str(e)}, returning unfiltered results")
                return career_pages[:criteria.get('num_results', 20)]
                
        except Exception as e:
            st.error(f"AI filtering error: {str(e)}")
            return career_pages[:criteria.get('num_results', 20)]
    
    def filter_jobs_with_gpt(self, jobs: List[Dict], criteria: Dict) -> List[Dict]:
        """Use Azure OpenAI GPT to filter and rank jobs based on criteria"""
        if not self.azure_client or not jobs:
            if not self.azure_client:
                st.warning("Azure OpenAI not configured. Returning unfiltered results.")
            return jobs[:criteria.get('num_results', 10)]
        
        try:
            # Prepare job data for GPT
            job_summaries = []
            for i, job in enumerate(jobs[:50]):  # Limit to first 50 jobs for API efficiency
                summary = f"""
                Job {i+1}:
                Title: {job['title']}
                Company: {job['company']}
                Location: {job['location']}
                Description: {job['description'][:500]}...
                Employment Type: {job.get('schedule_type', 'Not specified')}
                Remote: {job.get('work_from_home', 'Not specified')}
                """
                job_summaries.append(summary)
            
            # Create GPT prompt
            prompt = f"""
            You are a job recommendation expert. Please analyze these job listings and select the most relevant ones based on the following criteria:

            Criteria:
            - Position: {criteria.get('position', 'Any')}
            - Employment Type: {criteria.get('employment_type', 'Any')}
            - Work Mode: {criteria.get('work_mode', 'Any')}
            - Experience Level: {criteria.get('experience_level', 'Any')}
            - Location Preference: {criteria.get('location', 'Any')}
            - Number of results wanted: {criteria.get('num_results', 10)}

            Jobs to analyze:
            {chr(10).join(job_summaries[:20])}  # Limit for token efficiency

            Please return a JSON array with job numbers (1-based) that best match the criteria, ordered by relevance.
            Format: {{"selected_jobs": [1, 3, 5, 7, ...]}}
            Only return the JSON, no additional text.
            """

            # Make Azure OpenAI API call
            response = self.azure_client.chat.completions.create(
                model=self.azure_openai_deployment,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful job matching assistant. Always respond with valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            
            # Parse GPT response
            try:
                # Clean the response to extract JSON
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:-3]
                elif result.startswith("```"):
                    result = result[3:-3]
                
                parsed_result = json.loads(result)
                selected_indices = parsed_result.get("selected_jobs", [])
                
                # Convert 1-based indices to 0-based and filter jobs
                filtered_jobs = []
                for idx in selected_indices:
                    if 1 <= idx <= len(jobs):
                        filtered_jobs.append(jobs[idx-1])
                
                if filtered_jobs:
                    st.success(f"🤖 AI selected {len(filtered_jobs)} most relevant jobs from {len(jobs)} results")
                    return filtered_jobs[:criteria.get('num_results', 10)]
                else:
                    st.warning("AI filtering returned no results, showing original results")
                    return jobs[:criteria.get('num_results', 10)]
                
            except json.JSONDecodeError as e:
                st.warning(f"AI response parsing failed: {str(e)}, returning original results")
                return jobs[:criteria.get('num_results', 10)]
                
        except Exception as e:
            st.error(f"Azure OpenAI filtering error: {str(e)}")
            return jobs[:criteria.get('num_results', 10)]
    
    def display_jobs(self, jobs: List[Dict]):
        """Display job results in a formatted way"""
        if not jobs:
            st.info("No jobs found matching your criteria.")
            return
        
        st.markdown(f"### Found {len(jobs)} Jobs")
        
        for i, job in enumerate(jobs, 1):
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <h4>🎯 {job['title']}</h4>
                    <p><strong>🏢 Company:</strong> {job['company']}</p>
                    <p><strong>📍 Location:</strong> {job['location']}</p>
                    <p><strong>🕒 Posted:</strong> {job.get('posted_at', 'Recently')}</p>
                    <p><strong>💼 Type:</strong> {job.get('schedule_type', 'Not specified')}</p>
                    <p><strong>🏠 Remote:</strong> {'Yes' if job.get('work_from_home') else 'Not specified'}</p>
                    <p><strong>📝 Description:</strong> {job['description'][:500]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if job.get('link'):
                        st.markdown(f"[🔗 Apply Now]({job['link']})")
                with col2:
                    st.markdown(f"*Via: {job.get('via', 'Direct')}*")
                
                st.divider()
    
    def display_career_pages(self, career_pages: List[Dict]):
        """Display filtered career page results"""
        if not career_pages:
            st.info("No career pages found matching your criteria.")
            return
        
        st.markdown(f"### 🎯 {len(career_pages)} Validated Career Pages")
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            unique_domains = len(set(page['domain'] for page in career_pages))
            st.metric("🌐 Unique Domains", unique_domains)
        with col2:
            industries = set(page['industry'] for page in career_pages)
            st.metric("🏭 Industries", len(industries))
        with col3:
            company_sizes = set(page['company_size'] for page in career_pages)
            st.metric("📊 Company Types", len(company_sizes))
        
        # Display options
        display_mode = st.radio("Display Mode", ["Cards View", "Table View"], horizontal=True)
        
        if display_mode == "Cards View":
            # Group by industry or company size
            group_by = st.selectbox("Group by", ["Industry", "Company Size"], key="group_career")
            
            if group_by == "Industry":
                grouped = {}
                for page in career_pages:
                    industry = page['industry']
                    if industry not in grouped:
                        grouped[industry] = []
                    grouped[industry].append(page)
            else:
                grouped = {}
                for page in career_pages:
                    size = page['company_size']
                    if size not in grouped:
                        grouped[size] = []
                    grouped[size].append(page)
            
            for group_name, pages in grouped.items():
                with st.expander(f"📁 {group_name} ({len(pages)} companies)", expanded=True):
                    for page in pages:
                        st.markdown(f"""
                        <div class="company-card">
                            <h5>🏢 {page['company_name']}</h5>
                            <p><strong>🌐 Domain:</strong> {page['domain']}</p>
                            <p><strong>🏭 Industry:</strong> {page['industry']}</p>
                            <p><strong>📊 Size:</strong> {page['company_size']}</p>
                            <p><strong>📝 Description:</strong> {page['description'][:200]}...</p>
                            <p><a href="{page['career_url']}" target="_blank">🔗 Visit Career Page</a></p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("---")
        else:
            # Table view
            df_data = []
            for page in career_pages:
                df_data.append({
                    "Company": page['company_name'],
                    "Domain": page['domain'],
                    "Industry": page['industry'],
                    "Size": page['company_size'].split(" (")[0],  # Shorter display
                    "Career URL": page['career_url']
                })
            
            df = pd.DataFrame(df_data)
            
            # Add filtering options for table
            col1, col2 = st.columns(2)
            with col1:
                industry_filter = st.multiselect("Filter by Industry", df['Industry'].unique(), key="industry_filter")
            with col2:
                size_filter = st.multiselect("Filter by Size", df['Size'].unique(), key="size_filter")
            
            # Apply filters
            filtered_df = df.copy()
            if industry_filter:
                filtered_df = filtered_df[filtered_df['Industry'].isin(industry_filter)]
            if size_filter:
                filtered_df = filtered_df[filtered_df['Size'].isin(size_filter)]
            
            st.dataframe(filtered_df, use_container_width=True)
        
        # Export options
        st.markdown("### 📥 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Copy Career URLs"):
                urls = "\n".join([page['career_url'] for page in career_pages])
                st.code(urls, language="text")
        
        with col2:
            # Download as CSV
            df_export = pd.DataFrame(career_pages)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="💾 Download as CSV",
                data=csv,
                file_name=f"career_pages_{len(career_pages)}_results.csv",
                mime="text/csv"
            )
    
    def run(self):
        """Main application runner"""
        st.markdown('<h1 class="main-header">🔍 Job Hunter Pro</h1>', unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2 = st.tabs(["🎯 Job Search", "🏢 Company Career Pages"])
        
        with tab1:
            st.header("Smart Job Search")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                position = st.text_input("Position/Job Title", placeholder="Software Engineer, Data Scientist, etc.")
                location = st.text_input("Location", placeholder="San Francisco, Remote, etc.")
            
            with col2:
                employment_type = st.selectbox("Employment Type", ["Any"] + self.employment_types)
                work_mode = st.selectbox("Work Mode", ["Any"] + self.work_modes)
            
            col3, col4 = st.columns([1, 1])
            with col3:
                experience_level = st.selectbox("Experience Level", ["Any"] + self.experience_levels)
            with col4:
                num_results = st.slider("Number of Results", 5, 100, 20)
            
            use_gpt_filtering = st.checkbox("🤖 Use AI-Powered Job Filtering", value=True, 
                                          help="Uses Azure OpenAI GPT to intelligently filter jobs based on your criteria")
            
            if st.button("🔍 Search Jobs", type="primary"):
                if not position:
                    st.error("Please enter a position/job title")
                    return
                
                with st.spinner("Searching for jobs..."):
                    # Build search query
                    query_parts = [position]
                    if employment_type != "Any":
                        query_parts.append(employment_type.lower())
                    if work_mode == "Remote":
                        query_parts.append("remote")
                    
                    query = " ".join(query_parts)
                    
                    # Search jobs
                    jobs = self.search_serp_jobs(query, location, num_results)
                    
                    if jobs and use_gpt_filtering:
                        with st.spinner("AI is filtering the best matches for you..."):
                            criteria = {
                                "position": position,
                                "employment_type": employment_type,
                                "work_mode": work_mode,
                                "experience_level": experience_level,
                                "location": location,
                                "num_results": num_results
                            }
                            jobs = self.filter_jobs_with_gpt(jobs, criteria)
                    
                    # Display results
                    self.display_jobs(jobs)
        
        with tab2:
            st.header("Industry Career Pages Discovery")
            st.markdown("*Automatically discover career pages from companies in specific industries*")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_industry = st.selectbox(
                    "🏭 Select Industry Domain",
                    self.industry_domains,
                    help="Choose the industry to discover career pages from"
                )
                
                selected_company_size = st.selectbox(
                    "📊 Company Size Preference", 
                    self.company_sizes,
                    help="Choose between large corporations or startups"
                )
            
            with col2:
                num_career_results = st.slider("🎯 Number of Companies", 10, 100, 30, step=5)
                
                use_ai_validation = st.checkbox(
                    "🤖 AI Career Page Validation", 
                    value=True,
                    help="Use AI to validate and filter legitimate career pages"
                )
            
            # Advanced options in expandable section
            with st.expander("⚙️ Advanced Search Options"):
                col3, col4 = st.columns(2)
                with col3:
                    location_filter = st.text_input(
                        "🌍 Location Focus (Optional)",
                        placeholder="USA, Europe, Global, etc.",
                        help="Add location preference to the search"
                    )
                with col4:
                    exclude_keywords = st.text_input(
                        "🚫 Exclude Keywords (Optional)", 
                        placeholder="recruiter, consultant, agency",
                        help="Keywords to exclude from results"
                    )
            
            if st.button("🔍 Discover Career Pages", type="primary"):
                if not selected_industry:
                    st.error("Please select an industry domain")
                    return
                
                search_criteria = {
                    "industry": selected_industry,
                    "company_size": selected_company_size,
                    "num_results": num_career_results,
                    "location": location_filter,
                    "exclude_keywords": exclude_keywords
                }
                
                with st.spinner(f"🔍 Discovering career pages for {selected_industry} companies..."):
                    # Step 1: Discover career pages via SERP API
                    raw_career_pages = self.discover_career_pages_by_industry(
                        selected_industry, 
                        selected_company_size, 
                        num_career_results * 2  # Get more for better filtering
                    )
                    
                    if raw_career_pages:
                        # Step 2: Apply AI validation if enabled
                        if use_ai_validation and self.azure_client:
                            with st.spinner("🤖 AI is validating career pages and removing duplicates..."):
                                validated_pages = self.filter_career_pages_with_llm(
                                    raw_career_pages, 
                                    search_criteria
                                )
                                final_pages = validated_pages
                        else:
                            final_pages = raw_career_pages[:num_career_results]
                        
                        # Step 3: Display results
                        if final_pages:
                            self.display_career_pages(final_pages)
                            
                            # Show search summary
                            st.markdown("---")
                            st.markdown("### 📊 Search Summary")
                            col_sum1, col_sum2, col_sum3 = st.columns(3)
                            with col_sum1:
                                st.metric("🔍 Raw Results Found", len(raw_career_pages))
                            with col_sum2:
                                st.metric("✅ AI Validated Results", len(final_pages) if use_ai_validation else "N/A")
                            with col_sum3:
                                accuracy = f"{(len(final_pages)/len(raw_career_pages)*100):.1f}%" if raw_career_pages else "0%"
                                st.metric("🎯 Filter Accuracy", accuracy)
                        else:
                            st.warning("No career pages found matching your criteria. Try adjusting your search parameters.")
                    else:
                        st.error("No career pages discovered. Please try a different industry or search criteria.")
            
            # Show example searches
            with st.expander("💡 Example Search Combinations"):
                st.markdown("""
                **Popular Combinations:**
                - 🚀 **Technology & Software** + **Startups** → Discover emerging tech companies
                - 💰 **Financial Services** + **MNCs** → Find major banks and financial institutions
                - 🏥 **Healthcare & Biotechnology** + **MNCs** → Explore pharmaceutical giants
                - 🛒 **E-commerce & Retail** + **Startups** → Find growing online businesses
                - 🎮 **Gaming & Digital Entertainment** + **Startups** → Discover indie game studios
                
                **Pro Tips:**
                - Use **AI Validation** for higher quality results
                - Set **Location Focus** for region-specific companies
                - Add **Exclude Keywords** to filter out recruiters and agencies
                """)

        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Built by a drained Job Seeker - <a href="https://www.linkedin.com/in/sumant-pujari">Sumant Pujari</a></p>
        </div>
        """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    app = JobHunterApp()
    app.run()