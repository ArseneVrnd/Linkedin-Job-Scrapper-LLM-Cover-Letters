"""
LLM Helper for generating cover letters and customizing CV sections using Groq API
"""
from groq import Groq
from config import GROQ_API_KEY, COVER_LETTERS_DIR, CV_SECTIONS_DIR
import os
from datetime import datetime


class LLMHelper:
    def __init__(self, api_key=None):
        """
        Initialize Groq client
        
        Args:
            api_key (str): Groq API key (if None, uses config)
        """
        api_key = api_key or GROQ_API_KEY
        if not api_key:
            raise ValueError("Groq API key is required. Please provide it when initializing LLMHelper or set it in config.")
        
        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b"  # Using GPT-OSS-120B model on Groq

    def adapt_cover_letter(self, job_data, base_cover_letter, additional_context=None):
        """
        Adapt an existing cover letter to match a specific job description
        
        Args:
            job_data (dict): Job information dictionary
            base_cover_letter (str): The user's existing cover letter template
            additional_context (dict): Optional additional context (achievements, company research, motivation)
        
        Returns:
            str: Adapted cover letter
        """
        job_title = job_data.get('title', 'the position')
        company = job_data.get('company', 'your company')
        location = job_data.get('location', '')
        description = job_data.get('description_snippet', '')
        job_link = job_data.get('link', '')
        
        # Build additional context string
        context_parts = []
        if additional_context:
            if additional_context.get('achievements'):
                context_parts.append(f"Specific achievements or projects to highlight: {additional_context['achievements']}")
            if additional_context.get('company_research'):
                context_parts.append(f"Company research: {additional_context['company_research']}")
            if additional_context.get('motivation'):
                context_parts.append(f"Why I'm particularly interested in this role: {additional_context['motivation']}")
        
        additional_context_str = "\n".join(context_parts) if context_parts else "None"
        
        prompt = f"""PROMPT:
I need you to adapt my cover letter to perfectly match a job description I found on LinkedIn. Please analyze both documents and create a tailored cover letter that highlights the most relevant aspects of my experience for this specific position.

My current cover letter:
{base_cover_letter}

Job description from LinkedIn:
Job Title: {job_title}
Company: {company}
Location: {location}
Job Description: {description}
Job Link: {job_link}

Instructions:

1. Identify the key requirements, skills, and qualifications mentioned in the job description
2. Match them with relevant experiences and skills from my cover letter
3. Reorganize and rewrite my cover letter to emphasize the most relevant points for THIS specific position
4. Use keywords and terminology from the job description naturally throughout the letter
5. Maintain a professional tone that matches the company culture (as suggested by the job posting)
6. Keep the letter concise (ideally 3-4 paragraphs, maximum 1 page)
7. Include a strong opening that shows genuine interest in this specific role and company
8. Provide concrete examples that demonstrate I meet their requirements
9. End with a compelling call to action

Additional context (optional):
{additional_context_str}

Please provide the adapted cover letter in a format ready to copy and use in my application."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional career coach and cover letter writing expert specializing in tailoring cover letters to specific job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            adapted_cover_letter = response.choices[0].message.content
            return adapted_cover_letter
            
        except Exception as e:
            print(f"Error adapting cover letter: {e}")
            return f"Error adapting cover letter: {str(e)}"

    def customize_cv_about_me(self, job_data, current_about_me=None, entire_cv=None):
        """
        Customize the "About Me" section of a CV based on job requirements
        
        Args:
            job_data (dict): Job information dictionary
            current_about_me (str): Current "About Me" section text
            entire_cv (str): Optional entire CV content for better context
        
        Returns:
            str: Customized "About Me" section
        """
        job_title = job_data.get('title', 'the position')
        company = job_data.get('company', '')
        description = job_data.get('description_snippet', '')
        
        if not current_about_me:
            current_about_me = """I am a dedicated professional with a passion for excellence and a proven track record of success. 
            I bring strong analytical skills, effective communication, and a collaborative approach to every project."""
        
        # Build prompt with CV context if available
        cv_context = ""
        if entire_cv:
            cv_context = f"\n\nFull CV Context (for reference):\n{entire_cv[:2000]}"  # Limit CV context to avoid token limits
        
        prompt = f"""You are a professional CV/resume consultant. Customize the "About Me" section of a CV to better match a specific job opportunity.

Job Title: {job_title}
Company: {company}
Job Description: {description}

Current "About Me" Section:
{current_about_me}
{cv_context}

Task: Rewrite the "About Me" section to:
1. Highlight skills and experiences most relevant to this specific job
2. Use keywords from the job description naturally
3. Maintain authenticity and truthfulness - only reference experiences/skills that exist in the full CV
4. Keep it concise (3-4 sentences or 2-3 short paragraphs)
5. Show enthusiasm for this type of role
6. Emphasize value proposition for this specific position

The customized section should:
- Be tailored to this job without being generic
- Incorporate relevant keywords from the job description
- Maintain the professional tone
- Be specific and impactful
- Not exceed 150 words
- Only mention skills, experiences, or achievements that are actually in the CV

Customized "About Me" Section:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional CV/resume consultant specializing in tailoring resumes to specific job opportunities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            
            customized_section = response.choices[0].message.content
            return customized_section
            
        except Exception as e:
            print(f"Error customizing CV section: {e}")
            return f"Error customizing CV section: {str(e)}"

    def save_cover_letter(self, cover_letter, job_data, filename=None):
        """
        Save cover letter to a text file
        
        Args:
            cover_letter (str): Cover letter text
            job_data (dict): Job information
            filename (str): Optional filename
        
        Returns:
            str: File path where cover letter was saved
        """
        if not filename:
            company = job_data.get('company', 'company').replace(' ', '_').replace('/', '_')
            title = job_data.get('title', 'position').replace(' ', '_').replace('/', '_')[:30]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cover_letter_{company}_{title}_{timestamp}.txt"
        
        filepath = os.path.join(COVER_LETTERS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("ADAPTED COVER LETTER\n")
            f.write("="*80 + "\n\n")
            f.write(f"Job Title: {job_data.get('title', 'N/A')}\n")
            f.write(f"Company: {job_data.get('company', 'N/A')}\n")
            f.write(f"Location: {job_data.get('location', 'N/A')}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*80 + "\n\n")
            f.write(cover_letter)
            f.write("\n\n" + "="*80 + "\n")
            f.write(f"Job Link: {job_data.get('link', 'N/A')}\n")
        
        print(f"Cover letter saved to {filepath}")
        return filepath

    def save_cv_section(self, cv_section, job_data, filename=None):
        """
        Save customized CV section to a text file
        
        Args:
            cv_section (str): Customized CV section text
            job_data (dict): Job information
            filename (str): Optional filename
        
        Returns:
            str: File path where CV section was saved
        """
        if not filename:
            company = job_data.get('company', 'company').replace(' ', '_').replace('/', '_')
            title = job_data.get('title', 'position').replace(' ', '_').replace('/', '_')[:30]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cv_about_me_{company}_{title}_{timestamp}.txt"
        
        filepath = os.path.join(CV_SECTIONS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("CUSTOMIZED CV - ABOUT ME SECTION\n")
            f.write("="*80 + "\n\n")
            f.write(f"Job Title: {job_data.get('title', 'N/A')}\n")
            f.write(f"Company: {job_data.get('company', 'N/A')}\n")
            f.write(f"Location: {job_data.get('location', 'N/A')}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*80 + "\n\n")
            f.write("CUSTOMIZED 'ABOUT ME' SECTION:\n")
            f.write("-"*80 + "\n\n")
            f.write(cv_section)
            f.write("\n\n" + "="*80 + "\n")
            f.write(f"Job Link: {job_data.get('link', 'N/A')}\n")
        
        print(f"CV section saved to {filepath}")
        return filepath
