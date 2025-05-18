"""
Resume Intelligence System - Main Analysis Script

This script integrates all components of the Resume Intelligence System to analyze
a resume against a job description, providing comprehensive insights and visualizations.
"""

import json
import os
from pathlib import Path

from resume_intelligence.section_detector import SectionDetector
from resume_intelligence.skill_matcher import SkillMatcher
from resume_intelligence.project_validator import ProjectValidator
from resume_intelligence.visualizer import visualize_skill_alignment, visualize_project_validation


def load_text_file(file_path):

    try:
        # Get file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # For PDF and DOCX files, use the DocumentParser
        if file_ext in ['.pdf', '.docx']:
            from resume_intelligence.utils.document_parser import DocumentParser
            parser = DocumentParser()
            return parser.parse(file_path)
        # For text files, read directly
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: .pdf, .docx, .txt")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        print("Please check if the file exists and the path is correct.")
        raise
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        raise


def analyze_resume(resume_path, jd_path, output_dir='output'):

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load resume and job description
    resume_text = load_text_file(resume_path)
    jd_text = load_text_file(jd_path)
    
    print("\n1. Detecting resume sections...")
    # Detect resume sections
    section_detector = SectionDetector()
    sections = section_detector.detect_sections(resume_text)
    
    # Save sections to JSON
    sections_output_path = os.path.join(output_dir, 'sections.json')
    section_detector.save_sections(sections, sections_output_path)
    print(f"   Sections saved to {sections_output_path}")
    
    print("\n2. Matching skills to job description...")
    # Match skills to job description
    skill_matcher = SkillMatcher()
    skills_text = sections.get('Skills', '')
    alignment_results = skill_matcher.compute_alignment(skills_text, jd_text, sections)
    
    # Save alignment results to JSON
    alignment_output_path = os.path.join(output_dir, 'skill_alignment.json')
    skill_matcher.save_results(alignment_results, alignment_output_path)
    print(f"   Skill alignment results saved to {alignment_output_path}")
    
    # Visualize skill alignment
    alignment_viz_path = os.path.join(output_dir, 'skill_alignment.png')
    visualize_skill_alignment(alignment_results, alignment_viz_path)
    print(f"   Skill alignment visualization saved to {alignment_viz_path}")
    
    print("\n3. Validating projects...")
    # Validate projects
    project_validator = ProjectValidator()
    projects_text = sections.get('Projects', '')
    validation_results = project_validator.validate_projects(projects_text, skills_text)
    
    # Save validation results to JSON
    validation_output_path = os.path.join(output_dir, 'project_validation.json')
    with open(validation_output_path, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)
    print(f"   Project validation results saved to {validation_output_path}")
    
    # Visualize project validation
    validation_viz_path = os.path.join(output_dir, 'project_validation.png')
    visualize_project_validation(validation_results, validation_viz_path)
    print(f"   Project validation visualization saved to {validation_viz_path}")
    
    print("\n4. Generating summary report...")
    # Generate summary report
    generate_summary_report(alignment_results, validation_results, sections, 
                          os.path.join(output_dir, 'resume_analysis_report.md'))
    print(f"   Summary report saved to {os.path.join(output_dir, 'resume_analysis_report.md')}")
    
    print("\nAnalysis complete! All results saved to the 'output' directory.")


def generate_summary_report(alignment_results, validation_results, sections, output_path):

    overall_alignment = alignment_results.get('overall_alignment', 0)
    section_scores = alignment_results.get('section_scores', {})
    missing_skills = alignment_results.get('missing_skills', [])
    
    flagged_projects = validation_results.get('flagged_projects', [])
    project_scores = validation_results.get('project_scores', {})
    
    # Calculate average project score
    avg_project_score = sum(project_scores.values()) / len(project_scores) if project_scores else 0
    
    # Generate report
    report = []
    report.append("# Resume Analysis Report\n")
    
    # Overall assessment
    report.append("## Overall Assessment\n")
    report.append(f"Overall Alignment Score: **{overall_alignment:.2f}%**\n")
    
    if overall_alignment >= 70:
        assessment = "Strong match for the position"
    elif overall_alignment >= 50:
        assessment = "Moderate match for the position"
    else:
        assessment = "Weak match for the position"
    
    report.append(f"Assessment: **{assessment}**\n")
    
    # Section scores
    report.append("## Section Scores\n")
    for section, score in section_scores.items():
        if section != 'total_score':
            report.append(f"- {section}: {score:.2f}\n")
    
    # Missing skills
    report.append("## Missing Skills\n")
    if missing_skills:
        for skill in missing_skills[:10]:  # Show top 10 missing skills
            report.append(f"- {skill}\n")
        if len(missing_skills) > 10:
            report.append(f"- ... and {len(missing_skills) - 10} more\n")
    else:
        report.append("No critical skills missing.\n")
    
    # Project assessment
    report.append("## Project Assessment\n")
    report.append(f"Average Project Score: **{avg_project_score * 100:.2f}%**\n")
    
    # Top projects
    report.append("### Top Projects\n")
    sorted_projects = sorted(project_scores.items(), key=lambda x: x[1], reverse=True)
    for project, score in sorted_projects[:3]:  # Show top 3 projects
        report.append(f"- {project} (Score: {score * 100:.2f}%)\n")
    
    # Flagged projects
    if flagged_projects:
        report.append("### Flagged Projects\n")
        for project in flagged_projects[:5]:  # Show top 5 flagged projects
            report.append(f"- {project}\n")
        if len(flagged_projects) > 5:
            report.append(f"- ... and {len(flagged_projects) - 5} more\n")
    
    # Recommendations
    report.append("## Recommendations\n")
    
    if missing_skills:
        report.append("### Skills to Develop\n")
        for skill in missing_skills[:5]:  # Show top 5 skills to develop
            report.append(f"- {skill}\n")
    
    report.append("### Resume Improvements\n")
    if 'Projects' not in sections or not sections['Projects']:
        report.append("- Add relevant projects that demonstrate your technical skills\n")
    if 'Work Experience' not in sections or not sections['Work Experience']:
        report.append("- Add relevant work experience\n")
    if 'Skills' not in sections or not sections['Skills']:
        report.append("- Add a dedicated skills section\n")
    if 'Education' not in sections or not sections['Education']:
        report.append("- Add education details\n")
    
    # Write report to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))


if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Analyze a resume against a job description.")
    parser.add_argument("resume", help="Path to the resume file (PDF, DOCX, or TXT)")
    parser.add_argument("jd", help="Path to the job description file (PDF, DOCX, or TXT)")
    parser.add_argument("--output", "-o", default="output", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if files exist before proceeding
    resume_exists = os.path.isfile(args.resume)
    jd_exists = os.path.isfile(args.jd)
    
    if not resume_exists or not jd_exists:
        print("\nError: One or more input files not found.")
        
        # Check for sample files in the samples directory
        samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        available_samples = []
        
        if os.path.isdir(samples_dir):
            available_samples = [f for f in os.listdir(samples_dir) if f.endswith(".txt")]
        
        if available_samples:
            print("\nAvailable sample files in 'samples' directory:")
            for sample in available_samples:
                print(f"  - samples/{sample}")
            
            # Identify specific sample files for resume and job description
            sample_resume = "sample_resume.txt" if "sample_resume.txt" in available_samples else None
            sample_jd = "JD.txt" if "JD.txt" in available_samples else None
            sample_jd_alt = "sample_job_description.txt" if "sample_job_description.txt" in available_samples else None
            
            # Provide helpful example with correct file paths
            print("\nExample usage:")
            if sample_resume and (sample_jd or sample_jd_alt):
                jd_example = f"samples/{sample_jd}" if sample_jd else f"samples/{sample_jd_alt}"
                print(f"  python {os.path.basename(__file__)} samples/{sample_resume} {jd_example}")
            else:
                # Fallback to using any available text files
                print(f"  python {os.path.basename(__file__)} samples/{available_samples[0]} samples/{available_samples[-1]}")
            
            # If user tried to use 'resume.txt' which doesn't exist, suggest the correct file
            if args.resume == "samples/resume.txt" and sample_resume:
                print(f"\nNote: It seems you tried to use 'samples/resume.txt' which doesn't exist.")
                print(f"Try using 'samples/{sample_resume}' instead.")
        else:
            print("\nNo sample text files found in the 'samples' directory.")
        
        exit(1)
    
    # If files exist, proceed with analysis
    
    analyze_resume(args.resume, args.jd, args.output)