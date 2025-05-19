from typing import Dict, List, Tuple, Any  # Added Any
import asyncio  # Added asyncio import
from dataclasses import dataclass
import textwrap
import PyPDF2
import re
from credibility_engine import CredibilityEngine

@dataclass
class HRExplanation:
    """Structured explanation package for HR decision-making"""
    score_breakdown: Dict[str, Tuple[float, str]]
    key_strengths: List[Tuple[str, str]]
    critical_weaknesses: List[Tuple[str, str]]
    prediction_interpretation: str
    action_items: List[str]

class HRExplainabilityLayer:
    """Transforms technical scores into HR-friendly explanations"""
    
    def __init__(self):
        self.SKILL_IMPACT = {
            'github': {
                'high': ("Demonstrates production-grade code quality", 
                        "Indicates real-world problem-solving ability"),
                'low': ("Limited evidence of practical coding", 
                       "May struggle with collaborative development")
            },
            'leetcode': {
                'high': ("Strong algorithmic thinking", 
                        "Quickly adapts to new technical challenges"),
                'low': ("May need support with complex problems", 
                       "Could require more training time")
            },
            'certifications': {
                'high': ("Validated specialized knowledge", 
                        "Shows commitment to professional growth"),
                'low': ("Knowledge gaps may exist", 
                       "May need more structured onboarding")
            },
            'resume': {
                'high': ("Excellent professional presentation",
                        "Shows strong communication skills"),
                'low': ("Needs improvement in presentation",
                       "May indicate weak communication")
            },
            'linkedin': {
                'high': ("Strong professional network",
                        "Demonstrates industry engagement"),
                'low': ("Limited professional presence",
                       "May lack industry connections")
            }
        }
        self.credibility_engine = CredibilityEngine()

    async def analyze_candidate(self, pdf_path: str, candidate_name: str) -> Dict[str, Any]:
        """Complete candidate analysis with credential verification"""
        # Get basic scores
        scores = self.parse_resume_pdf(pdf_path)
        
        # Extract URLs and certificates from resume
        candidate_data = self._extract_verification_data(pdf_path)
        
        # Verify credentials
        credibility_results = await self.credibility_engine.verify_all_credentials(candidate_data)
        
        # Adjust scores based on verification results
        verified_scores = self._adjust_scores_with_verification(scores, credibility_results)
        
        # Generate report
        report = self.generate_hr_report(verified_scores, candidate_name)
        
        return {
            'scores': verified_scores,
            'credibility_results': credibility_results,
            'report': report
        }

    def _extract_verification_data(self, pdf_path: str) -> Dict[str, Any]:
        """Extract verifiable information from resume"""
        try:
            verification_data = {
                'github_url': None,
                'leetcode_url': None,
                'linkedin_url': None,
                'certificates': []
            }
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

            # Extract GitHub URL
            github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
            if github_match:
                verification_data['github_url'] = f"https://{github_match.group()}"

            # Extract LeetCode URL
            leetcode_match = re.search(r'leetcode\.com/[\w-]+', text, re.IGNORECASE)
            if leetcode_match:
                verification_data['leetcode_url'] = f"https://{leetcode_match.group()}"

            # Extract LinkedIn URL
            linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
            if linkedin_match:
                verification_data['linkedin_url'] = f"https://{linkedin_match.group()}"

            # Extract certificates
            cert_pattern = r'(certification|certificate):\s*([^\n]+)'
            cert_matches = re.finditer(cert_pattern, text, re.IGNORECASE)
            for match in cert_matches:
                verification_data['certificates'].append({
                    'name': match.group(2).strip(),
                    'verification_url': None  # Would need specific logic per certification provider
                })

            return verification_data

        except Exception as e:
            print(f"Error extracting verification data: {str(e)}")
            return {
                'github_url': None,
                'leetcode_url': None,
                'linkedin_url': None,
                'certificates': []
            }

    def _adjust_scores_with_verification(self, scores: Dict[str, float], 
                                       verification_results: Dict[str, Any]) -> Dict[str, float]:
        """Adjust scores based on verification results"""
        try:
            adjusted_scores = scores.copy()
            
            # Adjust GitHub score
            if verification_results.get('github_verification') and \
               verification_results['github_verification'].is_valid:
                adjusted_scores['github'] = min(100, scores['github'] * 
                                             (1 + verification_results['github_verification'].confidence_score))
            elif 'github' in scores:
                adjusted_scores['github'] *= 0.5  # Penalize unverified profiles
            
            # Adjust LinkedIn score
            if verification_results.get('linkedin_verification') and \
               verification_results['linkedin_verification'].is_valid:
                adjusted_scores['linkedin'] = min(100, scores['linkedin'] * 
                                               (1 + verification_results['linkedin_verification'].confidence_score))
            elif 'linkedin' in scores:
                adjusted_scores['linkedin'] *= 0.7
            
            # Adjust certification scores
            if verification_results.get('certificate_verifications'):
                verified_count = sum(1 for cert in verification_results['certificate_verifications'] 
                                   if cert.is_valid)
                if verified_count > 0:
                    adjusted_scores['certifications'] = min(100, scores['certifications'] * 
                                                         (1 + (verified_count * 0.2)))
                else:
                    adjusted_scores['certifications'] *= 0.6
            
            return adjusted_scores
            
        except Exception as e:
            print(f"Error adjusting scores: {str(e)}")
            return scores  # Return original scores if adjustment fails

    def explain(self, scores: Dict[str, float]) -> HRExplanation:
        """Generate complete HR explanation package"""
        return HRExplanation(
            score_breakdown=self._explain_scores(scores),
            key_strengths=self._identify_strengths(scores),
            critical_weaknesses=self._identify_weaknesses(scores),
            prediction_interpretation=self._interpret_prediction(scores),
            action_items=self._generate_actions(scores)
        )

    def generate_hr_report(self, scores: Dict[str, float], candidate_name: str) -> str:
        """Generate ready-to-use HR report"""
        explanation = self.explain(scores)
        
        report = f"""
        HR DECISION REPORT: {candidate_name}
        {'=' * 50}
        
        SCORE BREAKDOWN:
        {self._format_score_breakdown(explanation.score_breakdown)}
        
        KEY STRENGTHS (Business Impact):
        {self._format_strengths(explanation.key_strengths)}
        
        CRITICAL WEAKNESSES (Risk Analysis):
        {self._format_weaknesses(explanation.critical_weaknesses)}
        
        PERFORMANCE PREDICTION:
        {textwrap.fill(explanation.prediction_interpretation, width=70)}
        
        RECOMMENDED ACTIONS:
        {self._format_actions(explanation.action_items)}
        """
        return textwrap.dedent(report).strip()

    def _explain_scores(self, scores: Dict[str, float]) -> Dict[str, Tuple[float, str]]:
        """Explain what each component score means in HR terms"""
        breakdown = {}
        for component, score in scores.items():
            if component in self.SKILL_IMPACT:
                level = 'high' if score >= 75 else 'low'
                impact = self.SKILL_IMPACT[component][level][0]
                breakdown[component] = (score, f"{impact} (Score: {score}/100)")
        return breakdown

    def _identify_strengths(self, scores: Dict[str, float]) -> List[Tuple[str, str]]:
        """Identify strengths with more inclusive thresholds"""
        strengths = []
        for component, score in scores.items():
            if component in self.SKILL_IMPACT and score >= 75:
                impact = self.SKILL_IMPACT[component]['high'][1]
                strengths.append((component, impact))
        return sorted(strengths, key=lambda x: -scores[x[0]])[:3]

    def _identify_weaknesses(self, scores: Dict[str, float]) -> List[Tuple[str, str]]:
        """Enhanced weakness detection with severity levels"""
        weaknesses = []
        for component, score in scores.items():
            if component in self.SKILL_IMPACT:
                if score < 60:  # Critical weakness
                    risk = f"CRITICAL: {self.SKILL_IMPACT[component]['low'][1]}"
                    weaknesses.append((component, risk))
                elif score < 70:  # Moderate weakness
                    risk = f"MODERATE: {self.SKILL_IMPACT[component]['low'][1]}"
                    weaknesses.append((component, risk))
        return sorted(weaknesses, key=lambda x: scores[x[0]])[:3]

    def _interpret_prediction(self, scores: Dict[str, float]) -> str:
        """Translate technical scores into performance prediction"""
        tech_avg = (scores.get('github', 0) + scores.get('leetcode', 0)) / 2
        prof_avg = (scores.get('resume', 0) + scores.get('linkedin', 0) + scores.get('certifications', 0)) / 3
        
        if tech_avg >= 80 and prof_avg >= 75:
            return ("High probability of immediate high performance. "
                   "Likely to contribute meaningfully within first 3 months.")
        elif tech_avg >= 75:
            return ("Strong technical contributor who may need 3-6 months "
                   "to reach full productivity in professional environment")
        else:
            return ("Expected to require 6+ months of onboarding and training "
                   "before reaching full productivity. Consider for junior roles.")

    def _generate_actions(self, scores: Dict[str, float]) -> List[str]:
        """Generate specific, complete action items with priority levels"""
        actions = []
        
        # Critical Technical Assessment
        if scores.get('github', 0) < 70:
            focus = "system architecture and design patterns" if scores['github'] < 60 else "code quality and best practices"
            actions.append(f"[HIGH] Conduct live coding assessment focusing on {focus}")
        
        if scores.get('leetcode', 0) < 70:
            level = "hard (system design)" if scores['leetcode'] < 60 else "medium (algorithms)"
            actions.append(f"[HIGH] Include {level} problems in technical screening")
        
        # Professional Development Assessment
        if scores.get('linkedin', 0) < 70:
            focus = ("profile completeness and basic professional presence" 
                    if scores['linkedin'] < 60 
                    else "industry networking and engagement quality")
            actions.append(f"[MEDIUM] Evaluate LinkedIn profile for {focus}")
        
        if scores.get('certifications', 0) < 70:
            focus = ("fundamental technical knowledge" 
                    if scores['certifications'] < 60 
                    else "specialized technical expertise")
            actions.append(f"[HIGH] Verify {focus} during technical interview")
        
        if scores.get('resume', 0) < 70:
            if scores['resume'] < 60:
                actions.append("[HIGH] Request significant resume improvements:\n" +
                             "  - Clear project descriptions\n" +
                             "  - Quantifiable achievements\n" +
                             "  - Technical skills validation")
            else:
                actions.append("[MEDIUM] Suggest resume enhancements:\n" +
                             "  - Highlight key achievements\n" +
                             "  - Add technical project details")
        
        # Additional Recommendations
        if any(scores.get(comp, 0) < 65 for comp in ['github', 'leetcode']):
            actions.append("[HIGH] Schedule additional technical screening round")
        
        if all(scores.get(comp, 0) >= 75 for comp in ['github', 'leetcode', 'certifications']):
            actions.append("[HIGH] Fast-track for senior technical interview")
        
        return actions if actions else ["[STANDARD] Proceed with regular interview process"]

    def _format_score_breakdown(self, breakdown: Dict[str, Tuple[float, str]]) -> str:
        return "\n".join(
            f"• {comp.upper()}: {exp}"
            for comp, (_, exp) in breakdown.items()
        )

    def _format_strengths(self, strengths: List[Tuple[str, str]]) -> str:
        """Format strengths with visual indicators"""
        return "\n".join(
            f"✓ {comp.upper()}: {impact}"
            for comp, impact in strengths
        )

    def _format_weaknesses(self, weaknesses: List[Tuple[str, str]]) -> str:
        """Format weaknesses with severity indicators"""
        formatted = []
        for comp, risk in weaknesses:
            severity, message = risk.split(':', 1)
            icon = '‼️' if 'CRITICAL' in severity else '⚠️'
            formatted.append(f"{icon} {comp.upper()}: {message.strip()}")
        return "\n".join(formatted)

    def _format_actions(self, actions: List[str]) -> str:
        """Format actions with priority indicators"""
        formatted = []
        for action in actions:
            if '[HIGH]' in action:
                formatted.append(f" {action.replace('[HIGH]', '')}")
            elif '[MEDIUM]' in action:
                formatted.append(f"{action.replace('[MEDIUM]', '')}")
            elif '[STANDARD]' in action:
                formatted.append(f" {action.replace('[STANDARD]', '')}")
            else:
                formatted.append(f"• {action}")
        return "\n".join(formatted)

    def parse_resume_pdf(self, pdf_path: str) -> Dict[str, float]:
        """Parse PDF resume and extract initial scores"""
        try:
            scores = {
                'github': 0,
                'leetcode': 0,
                'certifications': 0,
                'resume': 0,
                'linkedin': 0
            }
            
            # Read PDF content
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

            # Score resume format and content (basic metrics)
            scores['resume'] = self._score_resume_content(text)
            
            # Find and score GitHub/LeetCode profiles
            github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
            leetcode_match = re.search(r'leetcode\.com/[\w-]+', text, re.IGNORECASE)
            
            if (github_match):
                scores['github'] = 70  # Base score for having GitHub
            if (leetcode_match):
                scores['leetcode'] = 70  # Base score for having LeetCode
                
            # Check for certifications
            cert_keywords = ['certified', 'certification', 'certificate']
            if any(keyword in text.lower() for keyword in cert_keywords):
                scores['certifications'] = 70
                
            # Check LinkedIn
            linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
            if linkedin_match:
                scores['linkedin'] = 70

            return scores
            
        except Exception as e:
            print(f"Error parsing resume: {str(e)}")
            return scores

    def _score_resume_content(self, text: str) -> float:
        """Basic scoring of resume content"""
        score = 70.0  # Base score
        
        # Length check
        words = len(text.split())
        if words < 200:
            score -= 10
        elif words > 1000:
            score -= 5
            
        # Format checks
        has_sections = any(section in text.lower() for section in 
                          ['experience', 'education', 'skills', 'projects'])
        if has_sections:
            score += 10
            
        # Contact info check
        has_contact = any(contact in text.lower() for contact in 
                         ['email', 'phone', 'address'])
        if has_contact:
            score += 10
            
        return min(100.0, max(0.0, score))

async def main():
    try:
        explainer = HRExplainabilityLayer()
        
        # Parse and analyze PDF resume with verification
        pdf_path = "aparna.pdf"
        print(f"\nAnalyzing resume: {pdf_path}")
        
        # Full analysis with credential verification
        analysis = await explainer.analyze_candidate(pdf_path, "Aparna Mondal")
        
        print("\nCredibility Verification Results:")
        print(f"Overall Credibility Score: {analysis['credibility_results']['overall_credibility_score']}%")
        
        print("\nDetailed Report:")
        print(analysis['report'])
        
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())

