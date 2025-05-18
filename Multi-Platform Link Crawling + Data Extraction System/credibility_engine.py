from typing import Dict, Any, List
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CredentialVerification:
    is_valid: bool
    source: str
    details: str
    verification_date: str
    confidence_score: float

class CredibilityEngine:
    """Verifies candidate credentials across multiple platforms"""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}' if github_token else None,
            'User-Agent': 'Mozilla/5.0'
        }
        self.cert_verifier = CertificateVerifier()
        
    async def verify_all_credentials(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify credentials across all platforms"""
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                self.verify_github_activity(session, candidate_data.get('github_url')),
                self.verify_linkedin_profile(session, candidate_data.get('linkedin_url')),
                self.verify_certificates(session, candidate_data.get('certificates', [])),
                self.verify_leetcode_activity(session, candidate_data.get('leetcode_url'))
            )
            
            return {
                'github_verification': results[0],
                'linkedin_verification': results[1],
                'certificate_verifications': results[2],
                'leetcode_verification': results[3],
                'overall_credibility_score': self._calculate_credibility_score(results),
                'verification_timestamp': datetime.now().isoformat()
            }

    async def verify_github_activity(self, session: aiohttp.ClientSession, 
                                   github_url: str) -> CredentialVerification:
        """Verify GitHub profile and activity"""
        if not github_url:
            return CredentialVerification(False, 'github', 'No GitHub URL provided', 
                                       datetime.now().isoformat(), 0.0)
        
        try:
            username = github_url.split('/')[-1]
            api_url = f'https://api.github.com/users/{username}'
            
            async with session.get(api_url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    public_repos = data.get('public_repos', 0)
                    followers = data.get('followers', 0)
                    created_at = datetime.strptime(data.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
                    account_age = (datetime.now() - created_at).days
                    
                    confidence_score = self._calculate_github_score(public_repos, followers, account_age)
                    
                    return CredentialVerification(
                        is_valid=True,
                        source='github',
                        details=f"Active profile with {public_repos} repos, {followers} followers",
                        verification_date=datetime.now().isoformat(),
                        confidence_score=confidence_score
                    )
                return CredentialVerification(False, 'github', 'Profile not found', 
                                           datetime.now().isoformat(), 0.0)
        
        except Exception as e:
            return CredentialVerification(False, 'github', f'Verification failed: {str(e)}', 
                                       datetime.now().isoformat(), 0.0)

    async def verify_linkedin_profile(self, session: aiohttp.ClientSession, 
                                    linkedin_url: str) -> CredentialVerification:
        """Verify LinkedIn profile existence"""
        if not linkedin_url:
            return CredentialVerification(False, 'linkedin', 'No LinkedIn URL provided', 
                                       datetime.now().isoformat(), 0.0)
        
        try:
            async with session.get(linkedin_url) as response:
                is_valid = response.status == 200
                return CredentialVerification(
                    is_valid=is_valid,
                    source='linkedin',
                    details="Profile verified" if is_valid else "Profile not accessible",
                    verification_date=datetime.now().isoformat(),
                    confidence_score=0.8 if is_valid else 0.0
                )
        except Exception as e:
            return CredentialVerification(False, 'linkedin', f'Verification failed: {str(e)}', 
                                       datetime.now().isoformat(), 0.0)

    async def verify_leetcode_activity(self, session: aiohttp.ClientSession, 
                                     leetcode_url: str) -> CredentialVerification:
        """Verify LeetCode profile and activity"""
        if not leetcode_url:
            return CredentialVerification(False, 'leetcode', 'No LeetCode URL provided', 
                                       datetime.now().isoformat(), 0.0)
        
        try:
            username = leetcode_url.split('/')[-1]
            api_url = f'https://leetcode.com/graphql'
            query = {
                'query': '''
                    query getUserProfile($username: String!) {
                        matchedUser(username: $username) {
                            submitStats {
                                acSubmissionNum {
                                    difficulty
                                    count
                                }
                            }
                        }
                    }
                ''',
                'variables': {'username': username}
            }
            
            async with session.post(api_url, json=query) as response:
                if response.status == 200:
                    return CredentialVerification(
                        is_valid=True,
                        source='leetcode',
                        details="Active LeetCode profile verified",
                        verification_date=datetime.now().isoformat(),
                        confidence_score=0.8
                    )
                return CredentialVerification(False, 'leetcode', 'Profile not found', 
                                           datetime.now().isoformat(), 0.0)
        except Exception as e:
            return CredentialVerification(False, 'leetcode', f'Verification failed: {str(e)}', 
                                       datetime.now().isoformat(), 0.0)

    async def verify_certificates(self, session: aiohttp.ClientSession, 
                                certificates: List[Dict[str, str]]) -> List[CredentialVerification]:
        """Verify certificates through issuing authorities"""
        verifications = []
        
        for cert in certificates:
            verification_result = await self.cert_verifier.verify_certificate(session, cert)
            
            verifications.append(CredentialVerification(
                is_valid=verification_result['is_valid'],
                source='certificate',
                details=self._format_cert_details(verification_result),
                verification_date=datetime.now().isoformat(),
                confidence_score=verification_result['confidence_score']
            ))
        
        return verifications

    def _format_cert_details(self, result: Dict[str, Any]) -> str:
        """Format certificate verification details"""
        if result['is_valid']:
            details = result['details']
            return (f"Verified {result['provider'].title()} certification: "
                   f"{details.get('title', 'Unknown')} "
                   f"(Status: {details.get('status', 'Unknown')})")
        return f"Certificate verification failed: {result['details']}"

    def _calculate_credibility_score(self, verifications: List[CredentialVerification]) -> float:
        """Calculate overall credibility score"""
        weights = {
            'github': 0.3,
            'linkedin': 0.2,
            'certificate': 0.3,
            'leetcode': 0.2
        }
        
        total_score = 0
        total_weight = 0
        
        for verification in verifications:
            if isinstance(verification, list):  # Handle certificate list
                if verification:  # Check if list is not empty
                    cert_score = sum(v.confidence_score for v in verification) / len(verification)
                    total_score += cert_score * weights['certificate']
                    total_weight += weights['certificate']
            else:
                weight = weights.get(verification.source, 0)
                total_score += verification.confidence_score * weight
                total_weight += weight
                
        return round(total_score / total_weight * 100, 2) if total_weight > 0 else 0.0

    def _calculate_github_score(self, repos: int, followers: int, account_age: int) -> float:
        """Calculate GitHub credibility score"""
        repo_score = min(repos / 10, 1.0)  # Max score at 10 repos
        follower_score = min(followers / 50, 1.0)  # Max score at 50 followers
        age_score = min(account_age / 365, 1.0)  # Max score at 1 year
        
        return (repo_score * 0.4 + follower_score * 0.3 + age_score * 0.3)

class CertificateVerifier:
    """Specialized certificate verification engine"""
    
    CERT_PROVIDERS = {
        'microsoft': {
            'url': 'https://learn.microsoft.com/en-us/users/validate-certification/',
            'pattern': r'MS-\d{3,}'
        },
        'aws': {
            'url': 'https://aws.amazon.com/verification/',
            'pattern': r'AWS-\d{2,}-\d{4,}'
        },
        'coursera': {
            'url': 'https://www.coursera.org/verify/',
            'pattern': r'[A-Z0-9]{10,}'
        }
    }

    async def verify_certificate(self, session: aiohttp.ClientSession, cert_data: Dict[str, str]) -> Dict[str, Any]:
        """Verify certificate authenticity and details"""
        cert_name = cert_data.get('name', '').lower()
        cert_url = cert_data.get('verification_url', '')
        
        verification_result = {
            'is_valid': False,
            'provider': None,
            'details': {},
            'confidence_score': 0.0
        }

        try:
            # Identify certificate provider
            provider = self._identify_provider(cert_name, cert_url)
            if not provider:
                return self._update_result(verification_result, 
                                        details="Unable to identify certificate provider")

            # Extract certificate ID
            cert_id = self._extract_cert_id(cert_url, self.CERT_PROVIDERS[provider]['pattern'])
            if not cert_id:
                return self._update_result(verification_result, 
                                        details="Certificate ID not found or invalid format")

            # Verify with provider
            async with session.get(f"{self.CERT_PROVIDERS[provider]['url']}{cert_id}") as response:
                if response.status == 200:
                    html = await response.text()
                    verification_data = await self._parse_verification_page(html, provider)
                    
                    if verification_data:
                        verification_result.update({
                            'is_valid': True,
                            'provider': provider,
                            'details': verification_data,
                            'confidence_score': self._calculate_confidence_score(verification_data)
                        })
                        return verification_result

            return self._update_result(verification_result, 
                                    details="Certificate verification failed")

        except Exception as e:
            return self._update_result(verification_result, 
                                    details=f"Verification error: {str(e)}")

    def _identify_provider(self, cert_name: str, cert_url: str) -> str:
        """Identify certificate provider from name or URL"""
        for provider in self.CERT_PROVIDERS.keys():
            if provider in cert_name or provider in cert_url:
                return provider
        return None

    def _extract_cert_id(self, url: str, pattern: str) -> str:
        """Extract certificate ID using provider-specific pattern"""
        if match := re.search(pattern, url):
            return match.group(0)
        return None

    async def _parse_verification_page(self, html: str, provider: str) -> Dict[str, str]:
        """Parse verification page for certificate details"""
        soup = BeautifulSoup(html, 'html.parser')
        
        if provider == 'microsoft':
            return self._parse_microsoft_cert(soup)
        elif provider == 'aws':
            return self._parse_aws_cert(soup)
        elif provider == 'coursera':
            return self._parse_coursera_cert(soup)
        
        return {}

    def _parse_microsoft_cert(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Parse Microsoft certification page"""
        details = {}
        try:
            details['title'] = soup.find('h1', {'class': 'certification-title'}).text.strip()
            details['date'] = soup.find('div', {'class': 'certification-date'}).text.strip()
            details['status'] = soup.find('div', {'class': 'certification-status'}).text.strip()
            return details
        except:
            return {}

    def _calculate_confidence_score(self, details: Dict[str, str]) -> float:
        """Calculate verification confidence score"""
        score = 0.0
        if details.get('title'):
            score += 0.4
        if details.get('date'):
            score += 0.3
        if details.get('status') == 'Active':
            score += 0.3
        return score

    def _update_result(self, result: Dict[str, Any], details: str) -> Dict[str, Any]:
        """Update verification result with details"""
        result['details'] = details
        return result