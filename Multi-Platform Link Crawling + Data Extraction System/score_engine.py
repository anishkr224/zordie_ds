from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import openai

class ScoreGrade(Enum):
    A = (90, 100, "Excellent")
    B = (80, 89, "Very Good")
    C = (70, 79, "Good")
    D = (60, 69, "Fair")
    F = (0, 59, "Needs Improvement")

    @classmethod
    def get_grade(cls, score: float) -> 'ScoreGrade':
        for grade in cls:
            if grade.value[0] <= score <= grade.value[1]:
                return grade
        return cls.F

@dataclass
class ComponentWeight:
    weight: float
    description: str
    importance: str

class PlatformScorer:
    def __init__(self, openai_key: str):
        self.openai_key = openai_key
        openai.api_key = openai_key

    def calculate_leetcode_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate algorithmic score based on LeetCode profile."""
        try:
            problems_solved = profile_data.get('total_problems_solved', 0)
            contest_rating = profile_data.get('contest_rating', 0)
            hard_problems = profile_data.get('hard_problems_solved', 0)
            
            # Weighted calculation
            score = (
                (problems_solved / 500) * 40 +  # Max 40 points for problems
                (min(contest_rating, 2500) / 2500) * 40 +  # Max 40 points for rating
                (hard_problems / 100) * 20  # Max 20 points for hard problems
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def calculate_kaggle_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate data science depth score based on Kaggle profile."""
        try:
            competitions = profile_data.get('competition_medals', {})
            notebooks = profile_data.get('notebook_medals', {})
            
            score = (
                competitions.get('gold', 0) * 20 +
                competitions.get('silver', 0) * 15 +
                competitions.get('bronze', 0) * 10 +
                notebooks.get('gold', 0) * 10 +
                notebooks.get('silver', 0) * 7.5 +
                notebooks.get('bronze', 0) * 5
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def calculate_design_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate creative score based on Figma/Dribbble profile."""
        try:
            likes = profile_data.get('total_likes', 0)
            followers = profile_data.get('followers', 0)
            projects = profile_data.get('total_projects', 0)
            
            score = (
                (min(likes, 1000) / 1000) * 40 +
                (min(followers, 500) / 500) * 30 +
                (min(projects, 30) / 30) * 30
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def calculate_linkedin_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate social trust score based on LinkedIn profile."""
        try:
            connections = profile_data.get('connections', 0)
            endorsements = profile_data.get('endorsements', 0)
            posts = profile_data.get('posts_last_year', 0)
            
            score = (
                (min(connections, 500) / 500) * 40 +
                (min(endorsements, 100) / 100) * 40 +
                (min(posts, 50) / 50) * 20
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def calculate_cert_score(self, certifications: List[Dict[str, Any]]) -> float:
        """Calculate certification score."""
        try:
            cert_weights = {
                'professional': 25,
                'associate': 15,
                'fundamental': 10
            }
            
            score = sum(
                cert_weights.get(cert.get('level', 'fundamental'), 5)
                for cert in certifications
            )
            return min(100.0, score)
        except Exception:
            return 0.0

class MultiPlatformScorer:
    def __init__(self, openai_key: str, github_token: str):
        self.client = openai.OpenAI(api_key=openai_key)
        self.github_token = github_token
        self.weights = {
            'github': ComponentWeight(0.3, "Technical implementation skills", "Critical"),
            'leetcode': ComponentWeight(0.2, "Algorithmic problem-solving", "High"),
            'certifications': ComponentWeight(0.2, "Professional qualifications", "High"),
            'design': ComponentWeight(0.1, "Creative capabilities", "Medium"),
            'resume': ComponentWeight(0.1, "Professional presentation", "Medium"),
            'linkedin': ComponentWeight(0.1, "Professional networking", "Medium")
        }

    def calculate_final_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final weighted score from all components."""
        component_scores = {
            'github': self._calculate_github_score(data.get('github_analysis', {})),
            'leetcode': self._calculate_leetcode_score(data.get('leetcode_data', {})),
            'certifications': self._calculate_cert_score(data.get('certifications', [])),
            'design': self._calculate_design_score(data.get('design_data', {})),
            'resume': data.get('resume_score', {}).get('score', 0),
            'linkedin': self._calculate_linkedin_score(data.get('linkedin_data', {}))
        }

        final_score = sum(
            score * self.weights[platform].weight 
            for platform, score in component_scores.items()
        )

        grade = ScoreGrade.get_grade(final_score)
        
        return {
            'final_score': final_score,
            'grade': grade.name,
            'grade_description': grade.value[2],
            'component_scores': component_scores,
            'weights': {k: v.weight for k, v in self.weights.items()},
            'importance_levels': {k: v.importance for k, v in self.weights.items()},
            'explanations': self._generate_explanations(component_scores),
            'strengths': self._identify_strengths(component_scores),
            'areas_for_improvement': self._identify_improvements(component_scores)
        }

    def _calculate_github_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate GitHub technical score."""
        technical_score = github_data.get('average_technical_score', 0)
        repo_count = len(github_data.get('repositories', []))
        
        # Adjust score based on repository count
        if repo_count >= 5:
            technical_score *= 1.1
        elif repo_count <= 2:
            technical_score *= 0.9
            
        return min(100.0, technical_score)

    def _calculate_leetcode_score(self, leetcode_data: Dict[str, Any]) -> float:
        """Calculate LeetCode algorithmic score."""
        total_solved = leetcode_data.get('total_problems_solved', 0)
        hard_solved = leetcode_data.get('hard_problems_solved', 0)
        contest_rating = leetcode_data.get('contest_rating', 0)
        
        base_score = min(100, (total_solved / 500) * 100)
        hard_bonus = min(20, (hard_solved / 50) * 20)
        rating_bonus = min(20, (contest_rating / 2000) * 20)
        
        return min(100.0, base_score + hard_bonus + rating_bonus)

    def _calculate_cert_score(self, certifications: List[Dict[str, Any]]) -> float:
        """Calculate certification score."""
        try:
            cert_weights = {
                'professional': 25,
                'associate': 15,
                'fundamental': 10
            }
            
            score = sum(
                cert_weights.get(cert.get('level', 'fundamental'), 5)
                for cert in certifications
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def _calculate_design_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate creative score based on Figma/Dribbble profile."""
        try:
            likes = profile_data.get('total_likes', 0)
            followers = profile_data.get('followers', 0)
            projects = profile_data.get('total_projects', 0)
            
            score = (
                (min(likes, 1000) / 1000) * 40 +
                (min(followers, 500) / 500) * 30 +
                (min(projects, 30) / 30) * 30
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def _calculate_linkedin_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate social trust score based on LinkedIn profile."""
        try:
            connections = profile_data.get('connections', 0)
            endorsements = profile_data.get('endorsements', 0)
            posts = profile_data.get('posts_last_year', 0)
            
            score = (
                (min(connections, 500) / 500) * 40 +
                (min(endorsements, 100) / 100) * 40 +
                (min(posts, 50) / 50) * 20
            )
            return min(100.0, score)
        except Exception:
            return 0.0

    def _generate_explanations(self, scores: Dict[str, float]) -> Dict[str, str]:
        """Generate detailed explanations for each score component."""
        explanations = {}
        for platform, score in scores.items():
            grade = ScoreGrade.get_grade(score)
            weight = self.weights[platform]
            explanations[platform] = (
                f"{platform.title()} Score: {score:.1f}/100 (Grade {grade.name})\n"
                f"Importance: {weight.importance}\n"
                f"Impact: {weight.weight*100}% of final score\n"
                f"This indicates {grade.value[2].lower()} {weight.description}."
            )
        return explanations

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify key strengths based on scores."""
        strengths = []
        for platform, score in scores.items():
            if score >= 80:
                strengths.append(
                    f"Strong {self.weights[platform].description.lower()} "
                    f"({score:.1f}/100)"
                )
        return strengths

    def _identify_improvements(self, scores: Dict[str, float]) -> List[str]:
        """Identify areas needing improvement."""
        improvements = []
        for platform, score in scores.items():
            if score < 70:
                improvements.append(
                    f"Improve {self.weights[platform].description.lower()} "
                    f"(currently {score:.1f}/100)"
                )
        return improvements