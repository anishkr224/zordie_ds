import ast
import os
import openai
from typing import Dict, Any, List
from git import Repo
import radon.complexity as cc
import git
import tempfile
import shutil

# Configure git executable path
git.refresh(r"C:\Program Files\Git\cmd\git.exe")

class GitHubAnalyzer:
    def __init__(self, openai_key: str):
        self.openai_key = openai_key
        openai.api_key = openai_key
        self.temp_dir = None

    def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """Analyze a GitHub repository and return metrics."""
        try:
            # Create temporary directory for cloning
            self.temp_dir = tempfile.mkdtemp()
            print(f"Cloning repository: {repo_url}")
            
            # Clone repository
            repo = Repo.clone_from(repo_url, self.temp_dir)
            
            # Analyze code
            complexity_metrics = self._analyze_complexity()
            ast_metrics = self._analyze_ast_structure()
            code_quality = self._assess_code_quality(complexity_metrics)
            originality = self._check_originality()
            
            # Calculate technical score
            technical_score = self._calculate_technical_score(
                complexity_metrics, 
                ast_metrics,
                code_quality
            )
            
            return {
                "technical_score": technical_score,
                "code_quality_grade": code_quality,
                "originality_percentage": originality,
                "metrics": {
                    "complexity": complexity_metrics,
                    "ast_metrics": ast_metrics,
                    "code_quality": {
                        "maintainability": code_quality,
                        "documentation": self._assess_documentation()
                    }
                }
            }
        except Exception as e:
            print(f"Error analyzing repository: {str(e)}")
            return {
                "technical_score": 0.0,
                "code_quality_grade": "F",
                "originality_percentage": 0.0,
                "metrics": {}
            }
        finally:
            # Cleanup temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def _analyze_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity using radon."""
        total_complexity = 0
        file_count = 0
        
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file)) as f:
                            code = f.read()
                            complexity = cc.cc_visit(code)
                            total_complexity += sum(block.complexity for block in complexity)
                            file_count += 1
                    except Exception as e:
                        print(f"Error analyzing {file}: {str(e)}")
        
        return {
            "average": total_complexity / max(file_count, 1),
            "files_analyzed": file_count
        }

    def _analyze_ast_structure(self) -> Dict[str, Any]:
        """Analyze AST structure of Python files."""
        metrics = {
            "class_count": 0,
            "function_count": 0,
            "complexity_score": 0
        }
        
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file)) as f:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    metrics["class_count"] += 1
                                elif isinstance(node, ast.FunctionDef):
                                    metrics["function_count"] += 1
                    except Exception as e:
                        print(f"Error parsing {file}: {str(e)}")
        
        return metrics

    def _assess_code_quality(self, complexity_metrics: Dict[str, Any]) -> str:
        """Assess code quality and return grade."""
        avg_complexity = complexity_metrics.get("average", 0)
        if avg_complexity <= 5:
            return "A"
        elif avg_complexity <= 10:
            return "B"
        elif avg_complexity <= 20:
            return "C"
        elif avg_complexity <= 30:
            return "D"
        return "F"

    def _check_originality(self) -> float:
        """Check code originality using OpenAI."""
        try:
            # Sample some code for analysis
            code_samples = []
            for root, _, files in os.walk(self.temp_dir):
                for file in files:
                    if file.endswith('.py'):
                        with open(os.path.join(root, file)) as f:
                            code_samples.append(f.read())
                            if len(code_samples) >= 3:  # Analyze up to 3 files
                                break
            
            if not code_samples:
                return 0.0
                
            # Use OpenAI to assess originality
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Analyze this code for originality. Score from 0-100%."
                }, {
                    "role": "user",
                    "content": "\n".join(code_samples[:3])
                }]
            )
            
            # Extract score from response
            score_text = response.choices[0].message.content
            try:
                score = float(score_text.split('%')[0])
                return min(100.0, max(0.0, score))
            except:
                return 70.0  # Default score if parsing fails
                
        except Exception as e:
            print(f"Error checking originality: {str(e)}")
            return 0.0

    def _assess_documentation(self) -> str:
        """Assess documentation quality."""
        doc_count = 0
        file_count = 0
        
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file)) as f:
                            tree = ast.parse(f.read())
                            file_count += 1
                            for node in ast.walk(tree):
                                if ast.get_docstring(node):
                                    doc_count += 1
                    except:
                        continue
        
        doc_ratio = doc_count / max(file_count, 1)
        if doc_ratio >= 0.8:
            return "A"
        elif doc_ratio >= 0.6:
            return "B"
        elif doc_ratio >= 0.4:
            return "C"
        elif doc_ratio >= 0.2:
            return "D"
        return "F"

    def _calculate_technical_score(self, complexity_metrics: Dict[str, Any], 
                                 ast_metrics: Dict[str, Any], 
                                 code_quality: str) -> float:
        """Calculate overall technical score."""
        # Convert code quality grade to number
        quality_scores = {"A": 95, "B": 85, "C": 75, "D": 65, "F": 55}
        quality_score = quality_scores.get(code_quality, 55)
        
        # Calculate complexity score (lower is better)
        complexity_score = 100 - min(complexity_metrics.get("average", 0) * 5, 50)
        
        # Calculate structure score
        structure_score = min(
            (ast_metrics.get("class_count", 0) * 5 + 
             ast_metrics.get("function_count", 0) * 3), 100)
        
        # Weighted average
        return (quality_score * 0.4 + 
                complexity_score * 0.3 + 
                structure_score * 0.3)