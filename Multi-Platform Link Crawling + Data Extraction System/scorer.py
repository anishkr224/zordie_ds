from typing import Dict, Any, List
from datetime import datetime
import re
from typing import Dict, Any, List
from datetime import datetime
import re

class ResumeScorer:
    def __init__(self):
        self.platform_weights = {
            "GitHub": 0.4,
            "LinkedIn": 0.3,
            "LeetCode": 0.2,
            "Figma": 0.1
        }

    def score_resume(self, resume_data: Dict[str, Any], profile_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive scores and recommendations for the resume and profiles."""
        scores = {
            "resume_score": self._score_resume_format(resume_data),
            "platform_scores": self._score_platforms(profile_data),
            "trustworthiness_flags": self._check_trustworthiness(resume_data, profile_data),
            "recommendations": []
        }

        # Calculate overall score
        scores["overall_score"] = self._calculate_overall_score(scores)
        
        # Generate recommendations
        scores["recommendations"] = self._generate_recommendations(scores)
        
        return scores

    def _score_resume_format(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score the resume formatting and content."""
        score = 100
        deductions = []
        
        # Check formatting issues
        for issue in resume_data.get("format_issues", []):
            score -= 5
            deductions.append(issue)
        
        # Check URL presence
        if not resume_data.get("urls"):
            score -= 10
            deductions.append("No professional profile URLs found")
        
        # Check text length
        text_length = len(resume_data.get("text", "").split())
        if text_length < 100:
            score -= 15
            deductions.append("Resume content is too brief")
        elif text_length > 1000:
            score -= 10
            deductions.append("Resume content is too verbose")
        
        return {
            "score": max(0, score),
            "deductions": deductions
        }

    def _score_platforms(self, profile_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score individual platform profiles."""
        platform_scores = {}
        
        for profile in profile_data:
            platform = profile.get("platform")
            if not platform:
                continue
                
            score = 100
            deductions = []
            metrics = profile.get("metrics", {})
            
            if platform == "GitHub":
                # Check repository count
                repos = metrics.get("repos_count")
                if repos is None:
                    repos = 0
                if repos < 3:
                    score -= 20
                    deductions.append("Low repository count")
                
                # Check stars
                stars = metrics.get("stars")
                if stars is None:
                    stars = 0
                if stars < 5:
                    score -= 10
                    deductions.append("Low number of stars")
                
                # Check last commit
                last_commit = metrics.get("last_commit")
                if last_commit:
                    last_commit_date = datetime.fromisoformat(last_commit.replace('Z', '+00:00'))
                    if (datetime.now() - last_commit_date).days > 90:
                        score -= 15
                        deductions.append("No recent GitHub activity")
            
            elif platform == "LinkedIn":
                # Check profile completeness
                completeness = metrics.get("profile_completeness")
                if completeness is None:
                    completeness = 0
                if completeness < 80:
                    score -= (100 - completeness)
                    deductions.append("Incomplete LinkedIn profile")
                
                # Check endorsements
                endorsements = metrics.get("endorsements", {})
                if endorsements is None:
                    endorsements = {}
                if len(endorsements) < 3:
                    score -= 10
                    deductions.append("Limited skill endorsements")
            
            elif platform == "LeetCode":
                # Check solved problems
                solved = metrics.get("solved_problems")
                if solved is None:
                    solved = 0
                if solved < 50:
                    score -= 20
                    deductions.append("Low number of solved problems")
                elif solved < 100:
                    score -= 10
                    deductions.append("Moderate number of solved problems")
                
                # Check acceptance rate
                acceptance_rate = metrics.get("acceptance_rate")
                if acceptance_rate is not None:
                    if acceptance_rate < 50:
                        score -= 15
                        deductions.append("Low acceptance rate")
                    elif acceptance_rate < 70:
                        score -= 5
                        deductions.append("Moderate acceptance rate")
                
                # Check difficulty distribution
                difficulty_stats = metrics.get("difficulty_stats", {})
                if difficulty_stats:
                    easy = difficulty_stats.get("Easy", 0)
                    medium = difficulty_stats.get("Medium", 0)
                    hard = difficulty_stats.get("Hard", 0)
                    
                    if easy < 20:
                        score -= 5
                        deductions.append("Low number of easy problems solved")
                    if medium < 10:
                        score -= 10
                        deductions.append("Low number of medium problems solved")
                    if hard < 5:
                        score -= 5
                        deductions.append("Low number of hard problems solved")
                    
                    # Check for balanced problem-solving
                    if easy > 0 and medium > 0 and hard > 0:
                        if easy / (easy + medium + hard) > 0.8:
                            score -= 5
                            deductions.append("Too many easy problems compared to medium/hard")
                
                # Check recent activity
                recent_activity = metrics.get("recent_activity", [])
                if not recent_activity:
                    score -= 10
                    deductions.append("No recent activity")
                
                # Check ranking
                ranking = metrics.get("ranking")
                if ranking is not None:
                    if ranking > 100000:
                        score -= 5
                        deductions.append("Low ranking")
                    elif ranking > 50000:
                        score -= 2
                        deductions.append("Moderate ranking")
            
            platform_scores[platform] = {
                "score": max(0, score),
                "deductions": deductions
            }
        
        return platform_scores

    def _check_trustworthiness(self, resume_data: Dict[str, Any], profile_data: List[Dict[str, Any]]) -> List[str]:
        """Check for potential trustworthiness issues."""
        flags = []
        
        # Check for URL consistency
        resume_urls = set(resume_data.get("urls", []))
        profile_urls = {p.get("url") for p in profile_data if p.get("url")}
        
        if not resume_urls.intersection(profile_urls):
            flags.append("Resume URLs don't match scraped profile URLs")
        
        # Check for activity consistency
        github_data = next((p for p in profile_data if p.get("platform") == "GitHub"), None)
        if github_data:
            metrics = github_data.get("metrics", {})
            repos_count = metrics.get("repos_count")
            if repos_count is None:
                repos_count = 0
            if repos_count > 0 and not metrics.get("last_commit"):
                flags.append("GitHub profile shows repositories but no commit history")
        
        return flags

    def _calculate_overall_score(self, scores: Dict[str, Any]) -> float:
        """Calculate the overall score based on resume and platform scores."""
        overall_score = 0
        total_weight = 0
        
        # Add resume score with 30% weight
        resume_score = scores["resume_score"]["score"]
        overall_score += resume_score * 0.3
        total_weight += 0.3
        
        # Add platform scores
        for platform, score_data in scores["platform_scores"].items():
            weight = self.platform_weights.get(platform, 0)
            overall_score += score_data["score"] * weight
            total_weight += weight
        
        # Normalize score
        if total_weight > 0:
            overall_score /= total_weight
        
        return round(overall_score, 2)

    def _generate_recommendations(self, scores: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scores and deductions."""
        recommendations = []
        
        # Resume recommendations
        for deduction in scores["resume_score"]["deductions"]:
            recommendations.append(f"Resume: {deduction}")
        
        # Platform-specific recommendations
        for platform, score_data in scores["platform_scores"].items():
            for deduction in score_data["deductions"]:
                recommendations.append(f"{platform}: {deduction}")
        
        # Trustworthiness recommendations
        for flag in scores["trustworthiness_flags"]:
            recommendations.append(f"Trust: {flag}")
        
        return recommendations 