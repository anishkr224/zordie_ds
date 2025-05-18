from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ComponentExplanation:
    score: float
    importance: str
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str

class ScoreExplainer:
    def __init__(self):
        print("Initializing rule-based explainer...")
        self.importance_levels = {
            'github': 'Critical - Technical implementation skills',
            'leetcode': 'High - Algorithmic problem-solving',
            'certifications': 'High - Professional qualifications',
            'design': 'Medium - Creative capabilities',
            'resume': 'Medium - Professional presentation',
            'linkedin': 'Medium - Professional networking'
        }

    def generate_explanations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable explanations for the analysis results."""
        explanations = {
            "overall_explanation": self._explain_overall_score(analysis_result),
            "resume_explanation": self._explain_resume_score(analysis_result),
            "platform_explanations": self._explain_platform_scores(analysis_result),
            "trust_explanation": self._explain_trust_flags(analysis_result)
        }
        return explanations

    def _explain_overall_score(self, analysis_result: Dict[str, Any]) -> str:
        """Generate explanation for the overall score."""
        score = analysis_result.get('overall_score', 0)
        
        if score >= 85:
            return "Exceptional candidate with strong technical skills and professional presence"
        elif score >= 70:
            return "Strong candidate with solid technical foundation"
        elif score >= 60:
            return "Competent candidate with room for growth"
        else:
            return "Entry-level candidate requiring development"

    def _explain_resume_score(self, analysis_result: Dict[str, Any]) -> str:
        """Generate explanation for resume score."""
        resume_data = analysis_result.get('resume_score', {})
        score = resume_data.get('score', 0)
        deductions = resume_data.get('deductions', [])
        
        explanation = f"Resume Score: {score}/100\n\n"
        if deductions:
            explanation += "Areas for improvement:\n"
            explanation += "\n".join(f"- {d}" for d in deductions)
            
        return explanation

    def _explain_platform_scores(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Generate explanations for platform-specific scores."""
        platform_scores = analysis_result.get('platform_scores', {})
        explanations = {}
        
        for platform, score in platform_scores.items():
            importance = self.importance_levels.get(platform, "Medium")
            explanations[platform] = self._generate_platform_explanation(platform, score, importance)
            
        return explanations

    def _explain_trust_flags(self, analysis_result: Dict[str, Any]) -> str:
        """Generate explanation for trustworthiness flags."""
        flags = analysis_result.get('trustworthiness_flags', [])
        if not flags:
            return "No trustworthiness issues identified"
            
        explanation = "Trustworthiness concerns:\n"
        explanation += "\n".join(f"- {flag}" for flag in flags)
        return explanation

    def _generate_platform_explanation(self, platform: str, score: float, importance: str) -> str:
        """Generate detailed explanation for a specific platform."""
        base_explanation = f"{platform.title()} ({importance})\nScore: {score}/100\n\n"
        
        if score >= 85:
            detail = "Shows exceptional capability"
        elif score >= 70:
            detail = "Demonstrates strong proficiency"
        elif score >= 60:
            detail = "Shows basic competency"
        else:
            detail = "Needs improvement"
            
        return f"{base_explanation}{detail}"

class HRExplainer:
    """Provides human-readable explanations of scores for HR professionals."""
    
    def __init__(self):
        self.importance_levels = {
            'github': 'Critical - Shows hands-on technical skills',
            'leetcode': 'High - Demonstrates problem-solving ability',
            'certifications': 'High - Validates professional knowledge',
            'design': 'Medium - Shows creativity and attention to detail',
            'resume': 'Medium - Professional presentation',
            'linkedin': 'Medium - Professional networking and presence'
        }

    def explain_score(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive explanations for HR."""
        final_score = result['final_score']
        
        explanations = {
            'summary': self._generate_summary(final_score),
            'components': self._explain_components(result),
            'key_findings': self._identify_key_findings(result),
            'hiring_recommendation': self._generate_recommendation(final_score),
            'next_steps': self._suggest_next_steps(result)
        }
        
        return explanations

    def _generate_summary(self, final_score: float) -> str:
        if final_score >= 85:
            return "Strong candidate with exceptional technical skills and professional presence"
        elif final_score >= 70:
            return "Solid candidate with good technical foundation and professional background"
        elif final_score >= 60:
            return "Potential candidate with areas needing development"
        else:
            return "Early career candidate requiring significant development"

    def _explain_components(self, result: Dict[str, Any]) -> Dict[str, ComponentExplanation]:
        explanations = {}
        
        for platform, score in result['component_scores'].items():
            strengths = []
            weaknesses = []
            
            if score >= 80:
                strengths.append(f"Strong {platform} presence")
            elif score <= 60:
                weaknesses.append(f"Limited {platform} activity")
                
            explanations[platform] = ComponentExplanation(
                score=score,
                importance=self.importance_levels[platform],
                strengths=strengths,
                weaknesses=weaknesses,
                recommendation=self._get_component_recommendation(platform, score)
            )
            
        return explanations

    def _identify_key_findings(self, result: Dict[str, Any]) -> List[str]:
        findings = []
        scores = result['component_scores']
        
        # Technical capability findings
        if scores['github'] >= 80 and scores['leetcode'] >= 75:
            findings.append("Strong technical capabilities demonstrated through code and problem-solving")
        
        # Professional development findings
        if scores['certifications'] >= 70:
            findings.append("Shows commitment to professional development through certifications")
        
        # Areas of concern
        low_scores = [k for k, v in scores.items() if v < 60]
        if low_scores:
            findings.append(f"Development needed in: {', '.join(low_scores)}")
            
        return findings

    def _generate_recommendation(self, final_score: float) -> str:
        if final_score >= 85:
            return "Strongly recommend for technical interview"
        elif final_score >= 70:
            return "Recommend for technical interview with focus on specific areas"
        elif final_score >= 60:
            return "Consider for junior positions with mentoring plan"
        else:
            return "Recommend gaining more experience before proceeding"

    def _suggest_next_steps(self, result: Dict[str, Any]) -> List[str]:
        steps = []
        scores = result['component_scores']
        
        if scores['github'] >= 75:
            steps.append("Review GitHub projects in technical interview")
        
        if scores['leetcode'] >= 70:
            steps.append("Include algorithmic problems in assessment")
            
        if any(score < 60 for score in scores.values()):
            steps.append("Discuss development plan for weaker areas")
            
        return steps

    def _get_component_recommendation(self, platform: str, score: float) -> str:
        if platform == 'github':
            return "Focus technical discussion on project implementations" if score >= 75 else "Review basic coding practices"
        elif platform == 'leetcode':
            return "Include advanced algorithms in assessment" if score >= 75 else "Focus on fundamental problem-solving"
        elif platform == 'linkedin':
            return "Verify professional references" if score >= 75 else "Request additional professional background"
        return "Standard evaluation recommended"