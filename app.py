import streamlit as st
import requests
import json
from openai import AzureOpenAI
import pandas as pd
from typing import List, Dict, Any
import time
from urllib.parse import urlparse

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
        with st.sidebar:
            st.header("🔑 API Configuration")
            
            # SERP API
            self.serp_api_key = st.text_input("SERP API Key", type="password", 
                                            help="Get your API key from serpapi.com")
            
            st.subheader("🤖 Azure OpenAI Configuration")
            self.azure_openai_api_key = st.text_input("Azure OpenAI API Key", type="password",
                                                     help="Your Azure OpenAI API key")
            self.azure_openai_endpoint = st.text_input("Azure OpenAI Endpoint",
                                                      placeholder="https://your-resource.openai.azure.com/",
                                                      help="Your Azure OpenAI endpoint URL")
            self.azure_openai_deployment = st.text_input("Deployment Name",
                                                        placeholder="gpt-35-turbo or gpt-4",
                                                        value="gpt-35-turbo",
                                                        help="Your deployed model name in Azure OpenAI")
            self.azure_openai_api_version = st.selectbox("API Version",
                                                        ["2024-02-15-preview", "2023-12-01-preview", "2023-05-15"],
                                                        index=0,
                                                        help="Azure OpenAI API version")
            
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
        self.top_companies = [
            "Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix", "Tesla",
            "Salesforce", "Adobe", "Oracle", "IBM", "Intel", "NVIDIA", "Cisco",
            "SAP", "VMware", "Uber", "Airbnb", "Twitter", "LinkedIn", "Spotify",
            "Dropbox", "Slack", "Zoom", "Shopify", "Square", "PayPal", "eBay",
            "Atlassian", "ServiceNow", "Workday", "Palantir", "Snowflake",
            "Databricks", "Unity", "Twilio", "DocuSign", "Okta", "Splunk"
        ]
        
        self.employment_types = [
            "Full-time", "Part-time", "Contract", "Internship", "Temporary"
        ]
        
        self.work_modes = [
            "Remote", "On-site", "Hybrid"
        ]
        
        self.experience_levels = [
            "Entry Level", "Mid Level", "Senior Level", "Executive"
        ]
    
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
    
    def get_company_career_pages(self, companies: List[str]) -> List[Dict]:
        """Get career page URLs for companies with improved search strategies"""
        if not self.serp_api_key:
            st.error("Please provide SERP API key")
            return []
        
        career_pages = []
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        # Multiple search strategies for better results
        search_strategies = [
            f"{{}}.com careers",
            f"{{}}.com jobs",
            f"{{}} careers site:careers.{{}}.com",
            f"{{}} jobs hiring",
            f"{{}} company careers page"
        ]
        
        for i, company in enumerate(companies):
            try:
                status_placeholder.text(f"🔍 Searching career pages for {company}...")
                company_found = False
                
                # Try multiple search strategies
                for strategy_template in search_strategies:
                    if company_found:
                        break
                        
                    # Format the query based on strategy
                    if "{{}}" in strategy_template:
                        query = strategy_template.format(company, company.lower().replace(' ', ''))
                    else:
                        query = strategy_template.format(company)
                    
                    params = {
                        "engine": "google",
                        "q": query,
                        "api_key": self.serp_api_key,
                        "num": 5,
                        "gl": "us",  # Country
                        "hl": "en"   # Language
                    }
                    
                    try:
                        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Debug: Show raw response for first company
                            if i == 0:
                                st.write(f"Debug - API Response Status: {response.status_code}")
                                st.write(f"Debug - Query used: {query}")
                                if "organic_results" in data:
                                    st.write(f"Debug - Found {len(data['organic_results'])} organic results")
                                else:
                                    st.write(f"Debug - Available keys: {list(data.keys())}")
                            
                            organic_results = data.get("organic_results", [])
                            
                            for result in organic_results:
                                link = result.get("link", "")
                                title = result.get("title", "")
                                snippet = result.get("snippet", "")
                                
                                # More flexible career page detection
                                career_keywords = [
                                    "career", "job", "hiring", "work", "employment", 
                                    "talent", "opportunity", "join", "apply", "vacancy"
                                ]
                                
                                # Check if this looks like a career page
                                is_career_page = (
                                    any(keyword in link.lower() for keyword in career_keywords) or
                                    any(keyword in title.lower() for keyword in career_keywords) or
                                    any(keyword in snippet.lower() for keyword in career_keywords[:5])  # More specific keywords for snippet
                                )
                                
                                # Additional check for company domain
                                company_domain_match = (
                                    company.lower().replace(' ', '') in link.lower() or
                                    company.lower() in link.lower()
                                )
                                
                                if is_career_page or company_domain_match:
                                    career_pages.append({
                                        "company": company,
                                        "title": title,
                                        "link": link,
                                        "snippet": snippet,
                                        "search_query": query
                                    })
                                    company_found = True
                                    break
                        
                        elif response.status_code == 429:
                            st.warning(f"Rate limited, waiting before next request...")
                            time.sleep(2)
                            
                        else:
                            if i == 0:  # Debug info for first company
                                st.write(f"Debug - HTTP Error: {response.status_code}")
                                st.write(f"Debug - Response: {response.text[:500]}")
                    
                    except requests.exceptions.Timeout:
                        st.warning(f"Timeout for {company}, trying next strategy...")
                        continue
                    except requests.exceptions.RequestException as e:
                        st.warning(f"Request error for {company}: {str(e)}")
                        continue
                
                # If no career page found, add a generic result
                if not company_found:
                    # Try to construct a likely career page URL
                    company_clean = company.lower().replace(' ', '').replace('.', '')
                    generic_urls = [
                        f"https://careers.{company_clean}.com",
                        f"https://jobs.{company_clean}.com",
                        f"https://www.{company_clean}.com/careers",
                        f"https://www.{company_clean}.com/jobs"
                    ]
                    
                    career_pages.append({
                        "company": company,
                        "title": f"{company} - Careers (Constructed URL)",
                        "link": generic_urls[0],  # Use the most common pattern
                        "snippet": f"Career opportunities at {company}. Visit their career page to explore current openings.",
                        "search_query": "constructed_url"
                    })
                
                progress_bar.progress((i + 1) / len(companies))
                time.sleep(0.2)  # Slightly longer delay to avoid rate limiting
                
            except Exception as e:
                st.warning(f"Error fetching career page for {company}: {str(e)}")
                # Add fallback entry
                career_pages.append({
                    "company": company,
                    "title": f"{company} - Careers",
                    "link": f"https://www.google.com/search?q={company}+careers",
                    "snippet": f"Search for {company} career opportunities",
                    "search_query": "error_fallback"
                })
        
        status_placeholder.text(f"✅ Completed! Found {len(career_pages)} career pages.")
        return career_pages
    
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
                    <p><strong>📝 Description:</strong> {job['description'][:200]}...</p>
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
        """Display career page results with enhanced information"""
        if not career_pages:
            st.info("No career pages found.")
            return
        
        st.markdown(f"### Found {len(career_pages)} Career Pages")
        
        # Show summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            found_pages = len([p for p in career_pages if p.get('search_query') not in ['constructed_url', 'error_fallback']])
            st.metric("🔍 Found via Search", found_pages)
        with col2:
            constructed_pages = len([p for p in career_pages if p.get('search_query') == 'constructed_url'])
            st.metric("🏗️ Constructed URLs", constructed_pages)
        with col3:
            error_pages = len([p for p in career_pages if p.get('search_query') == 'error_fallback'])
            st.metric("⚠️ Fallback Results", error_pages)
        
        # Group by company
        companies_dict = {}
        for page in career_pages:
            company = page['company']
            if company not in companies_dict:
                companies_dict[company] = []
            companies_dict[company].append(page)
        
        # Display options
        display_mode = st.radio("Display Mode", ["Expandable Cards", "Simple List"], horizontal=True)
        
        if display_mode == "Expandable Cards":
            for company, pages in companies_dict.items():
                # Determine the icon based on how the page was found
                page_type = pages[0].get('search_query', '')
                if page_type == 'constructed_url':
                    icon = "🏗️"
                elif page_type == 'error_fallback':
                    icon = "⚠️"
                else:
                    icon = "🔍"
                
                with st.expander(f"{icon} {company} ({len(pages)} page{'s' if len(pages) > 1 else ''})"):
                    for page in pages:
                        st.markdown(f"""
                        <div class="company-card">
                            <h5>{page['title']}</h5>
                            <p><strong>🔍 Search Query:</strong> {page.get('search_query', 'N/A')}</p>
                            <p><strong>📝 Description:</strong> {page['snippet'][:300]}...</p>
                            <p><a href="{page['link']}" target="_blank">🔗 Visit Career Page</a></p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            # Simple list view
            df_data = []
            for page in career_pages:
                page_type = page.get('search_query', '')
                source = "🔍 Found" if page_type not in ['constructed_url', 'error_fallback'] else ("🏗️ Constructed" if page_type == 'constructed_url' else "⚠️ Fallback")
                
                df_data.append({
                    "Company": page['company'],
                    "Source": source,
                    "Title": page['title'],
                    "Link": page['link']
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        
        # Download option
        if st.button("📥 Download Career Pages as CSV"):
            df_download = pd.DataFrame(career_pages)
            csv = df_download.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="career_pages.csv",
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
            st.header("Company Career Pages")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_companies = st.multiselect(
                    "Select Companies",
                    self.top_companies,
                    default=self.top_companies[:10],
                    help="Select companies to find their career pages"
                )
            
            with col2:
                st.markdown(f"**Total Companies:** {len(self.top_companies)}")
                st.markdown(f"**Selected:** {len(selected_companies)}")
            
            if st.button("🔍 Find Career Pages", type="primary"):
                if not selected_companies:
                    st.error("Please select at least one company")
                    return
                
                with st.spinner(f"Searching career pages for {len(selected_companies)} companies..."):
                    career_pages = self.get_company_career_pages(selected_companies)
                    self.display_career_pages(career_pages)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Built with ❤️ using Streamlit • Powered by SERP API & Azure OpenAI</p>
            <p><small>Make sure to add your API keys and Azure OpenAI configuration in the sidebar to get started!</small></p>
        </div>
        """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    app = JobHunterApp()
    app.run()