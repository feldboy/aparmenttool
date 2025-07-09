"""
CAPTCHA solver integration for bypassing anti-bot protection

This module provides integration with various CAPTCHA solving services
to handle challenges encountered during scraping.
"""

import time
import logging
import requests
from typing import Dict, Any, Optional
from enum import Enum
import base64
import json

from .config import CaptchaConfig, CaptchaSolver

logger = logging.getLogger(__name__)

class CaptchaType(Enum):
    """Supported CAPTCHA types"""
    IMAGE = "image"
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    FUNCAPTCHA = "funcaptcha"
    GEETESTV3 = "geetest_v3"

class CaptchaSolverService:
    """Base CAPTCHA solver service"""
    
    def __init__(self, config: CaptchaConfig):
        self.config = config
        self.api_key = config.api_key
        self.timeout = config.timeout
        self.retry_count = config.retry_count
        
    def solve_captcha(self, captcha_type: CaptchaType, **kwargs) -> Optional[str]:
        """Solve a CAPTCHA challenge"""
        raise NotImplementedError("Subclasses must implement solve_captcha")
    
    def get_balance(self) -> Optional[float]:
        """Get account balance"""
        raise NotImplementedError("Subclasses must implement get_balance")

class TwoCaptchaSolver(CaptchaSolverService):
    """2Captcha solver implementation"""
    
    BASE_URL = "http://2captcha.com"
    
    def solve_captcha(self, captcha_type: CaptchaType, **kwargs) -> Optional[str]:
        """Solve CAPTCHA using 2Captcha service"""
        try:
            if captcha_type == CaptchaType.IMAGE:
                return self._solve_image_captcha(**kwargs)
            elif captcha_type == CaptchaType.RECAPTCHA_V2:
                return self._solve_recaptcha_v2(**kwargs)
            elif captcha_type == CaptchaType.HCAPTCHA:
                return self._solve_hcaptcha(**kwargs)
            else:
                logger.error(f"Unsupported CAPTCHA type: {captcha_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return None
    
    def _solve_image_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """Solve image-based CAPTCHA"""
        try:
            # Encode image as base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Submit CAPTCHA
            submit_data = {
                'key': self.api_key,
                'method': 'base64',
                'body': image_b64,
                'numeric': kwargs.get('numeric', 0),
                'min_len': kwargs.get('min_len', 0),
                'max_len': kwargs.get('max_len', 0),
                'language': kwargs.get('language', 0),
                'textinstructions': kwargs.get('instructions', ''),
                'json': 1
            }
            
            response = requests.post(f"{self.BASE_URL}/in.php", data=submit_data, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                logger.error(f"CAPTCHA submission failed: {result.get('error_text')}")
                return None
            
            captcha_id = result.get('request')
            
            # Wait for solution
            return self._wait_for_solution(captcha_id)
            
        except Exception as e:
            logger.error(f"Error solving image CAPTCHA: {str(e)}")
            return None
    
    def _solve_recaptcha_v2(self, site_key: str, page_url: str, **kwargs) -> Optional[str]:
        """Solve reCAPTCHA v2"""
        try:
            # Submit reCAPTCHA
            submit_data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            # Add optional parameters
            if kwargs.get('invisible'):
                submit_data['invisible'] = 1
            if kwargs.get('enterprise'):
                submit_data['enterprise'] = 1
            if kwargs.get('data_s'):
                submit_data['data-s'] = kwargs['data_s']
            
            response = requests.post(f"{self.BASE_URL}/in.php", data=submit_data, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                logger.error(f"reCAPTCHA submission failed: {result.get('error_text')}")
                return None
            
            captcha_id = result.get('request')
            
            # Wait for solution
            return self._wait_for_solution(captcha_id)
            
        except Exception as e:
            logger.error(f"Error solving reCAPTCHA v2: {str(e)}")
            return None
    
    def _solve_hcaptcha(self, site_key: str, page_url: str, **kwargs) -> Optional[str]:
        """Solve hCaptcha"""
        try:
            # Submit hCaptcha
            submit_data = {
                'key': self.api_key,
                'method': 'hcaptcha',
                'sitekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.post(f"{self.BASE_URL}/in.php", data=submit_data, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                logger.error(f"hCaptcha submission failed: {result.get('error_text')}")
                return None
            
            captcha_id = result.get('request')
            
            # Wait for solution
            return self._wait_for_solution(captcha_id)
            
        except Exception as e:
            logger.error(f"Error solving hCaptcha: {str(e)}")
            return None
    
    def _wait_for_solution(self, captcha_id: str) -> Optional[str]:
        """Wait for CAPTCHA solution"""
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                # Check solution status
                response = requests.get(
                    f"{self.BASE_URL}/res.php",
                    params={'key': self.api_key, 'action': 'get', 'id': captcha_id, 'json': 1},
                    timeout=30
                )
                result = response.json()
                
                if result.get('status') == 1:
                    logger.info(f"CAPTCHA solved successfully: {captcha_id}")
                    return result.get('request')
                elif result.get('error_text') == 'CAPCHA_NOT_READY':
                    # Still processing, wait and try again
                    time.sleep(5)
                    continue
                else:
                    logger.error(f"CAPTCHA solving failed: {result.get('error_text')}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error checking CAPTCHA status: {str(e)}")
                time.sleep(5)
                continue
        
        logger.error(f"CAPTCHA solving timed out: {captcha_id}")
        return None
    
    def get_balance(self) -> Optional[float]:
        """Get account balance"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/res.php",
                params={'key': self.api_key, 'action': 'getbalance', 'json': 1},
                timeout=30
            )
            result = response.json()
            
            if result.get('status') == 1:
                return float(result.get('request', 0))
            else:
                logger.error(f"Failed to get balance: {result.get('error_text')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return None

class AntiCaptchaSolver(CaptchaSolverService):
    """Anti-Captcha solver implementation"""
    
    BASE_URL = "https://api.anti-captcha.com"
    
    def solve_captcha(self, captcha_type: CaptchaType, **kwargs) -> Optional[str]:
        """Solve CAPTCHA using Anti-Captcha service"""
        try:
            if captcha_type == CaptchaType.IMAGE:
                return self._solve_image_captcha(**kwargs)
            elif captcha_type == CaptchaType.RECAPTCHA_V2:
                return self._solve_recaptcha_v2(**kwargs)
            elif captcha_type == CaptchaType.HCAPTCHA:
                return self._solve_hcaptcha(**kwargs)
            else:
                logger.error(f"Unsupported CAPTCHA type: {captcha_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return None
    
    def _solve_image_captcha(self, image_data: bytes, **kwargs) -> Optional[str]:
        """Solve image-based CAPTCHA"""
        try:
            # Encode image as base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create task
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "body": image_b64,
                    "numeric": kwargs.get('numeric', 0),
                    "minLength": kwargs.get('min_len', 0),
                    "maxLength": kwargs.get('max_len', 0),
                    "comment": kwargs.get('instructions', '')
                }
            }
            
            response = requests.post(f"{self.BASE_URL}/createTask", json=task_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                logger.error(f"CAPTCHA submission failed: {result.get('errorDescription')}")
                return None
            
            task_id = result.get('taskId')
            
            # Wait for solution
            return self._wait_for_solution(task_id)
            
        except Exception as e:
            logger.error(f"Error solving image CAPTCHA: {str(e)}")
            return None
    
    def _solve_recaptcha_v2(self, site_key: str, page_url: str, **kwargs) -> Optional[str]:
        """Solve reCAPTCHA v2"""
        try:
            # Create task
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key,
                    "isInvisible": kwargs.get('invisible', False)
                }
            }
            
            response = requests.post(f"{self.BASE_URL}/createTask", json=task_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                logger.error(f"reCAPTCHA submission failed: {result.get('errorDescription')}")
                return None
            
            task_id = result.get('taskId')
            
            # Wait for solution
            return self._wait_for_solution(task_id)
            
        except Exception as e:
            logger.error(f"Error solving reCAPTCHA v2: {str(e)}")
            return None
    
    def _solve_hcaptcha(self, site_key: str, page_url: str, **kwargs) -> Optional[str]:
        """Solve hCaptcha"""
        try:
            # Create task
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "HCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            response = requests.post(f"{self.BASE_URL}/createTask", json=task_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                logger.error(f"hCaptcha submission failed: {result.get('errorDescription')}")
                return None
            
            task_id = result.get('taskId')
            
            # Wait for solution
            return self._wait_for_solution(task_id)
            
        except Exception as e:
            logger.error(f"Error solving hCaptcha: {str(e)}")
            return None
    
    def _wait_for_solution(self, task_id: int) -> Optional[str]:
        """Wait for CAPTCHA solution"""
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                # Check task status
                response = requests.post(
                    f"{self.BASE_URL}/getTaskResult",
                    json={"clientKey": self.api_key, "taskId": task_id},
                    timeout=30
                )
                result = response.json()
                
                if result.get('errorId') != 0:
                    logger.error(f"CAPTCHA solving failed: {result.get('errorDescription')}")
                    return None
                
                if result.get('status') == 'ready':
                    solution = result.get('solution', {})
                    logger.info(f"CAPTCHA solved successfully: {task_id}")
                    return solution.get('gRecaptchaResponse') or solution.get('text')
                elif result.get('status') == 'processing':
                    # Still processing, wait and try again
                    time.sleep(5)
                    continue
                else:
                    logger.error(f"Unknown CAPTCHA status: {result.get('status')}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error checking CAPTCHA status: {str(e)}")
                time.sleep(5)
                continue
        
        logger.error(f"CAPTCHA solving timed out: {task_id}")
        return None
    
    def get_balance(self) -> Optional[float]:
        """Get account balance"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/getBalance",
                json={"clientKey": self.api_key},
                timeout=30
            )
            result = response.json()
            
            if result.get('errorId') == 0:
                return float(result.get('balance', 0))
            else:
                logger.error(f"Failed to get balance: {result.get('errorDescription')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return None

def get_captcha_solver(config: CaptchaConfig) -> Optional[CaptchaSolverService]:
    """Get CAPTCHA solver instance based on configuration"""
    if config.solver == CaptchaSolver.TWOCAPTCHA:
        return TwoCaptchaSolver(config)
    elif config.solver == CaptchaSolver.ANTICAPTCHA:
        return AntiCaptchaSolver(config)
    else:
        logger.error(f"Unsupported CAPTCHA solver: {config.solver}")
        return None

def detect_captcha_type(html_content: str) -> Optional[CaptchaType]:
    """Detect CAPTCHA type from HTML content"""
    html_lower = html_content.lower()
    
    # Check for reCAPTCHA
    if 'recaptcha' in html_lower or 'g-recaptcha' in html_lower:
        return CaptchaType.RECAPTCHA_V2
    
    # Check for hCaptcha
    if 'hcaptcha' in html_lower or 'h-captcha' in html_lower:
        return CaptchaType.HCAPTCHA
    
    # Check for FunCaptcha
    if 'funcaptcha' in html_lower or 'arkoselabs' in html_lower:
        return CaptchaType.FUNCAPTCHA
    
    # Check for image CAPTCHA
    if ('captcha' in html_lower and 
        ('img' in html_lower or 'image' in html_lower)):
        return CaptchaType.IMAGE
    
    return None

def extract_captcha_parameters(html_content: str, captcha_type: CaptchaType) -> Dict[str, Any]:
    """Extract CAPTCHA parameters from HTML content"""
    import re
    
    params = {}
    
    if captcha_type == CaptchaType.RECAPTCHA_V2:
        # Extract site key
        site_key_match = re.search(r'data-sitekey=[\'"]([\w-]+)[\'"]', html_content, re.I)
        if site_key_match:
            params['site_key'] = site_key_match.group(1)
        
        # Check if invisible
        if 'data-size="invisible"' in html_content.lower():
            params['invisible'] = True
    
    elif captcha_type == CaptchaType.HCAPTCHA:
        # Extract site key
        site_key_match = re.search(r'data-sitekey=[\'"]([\w-]+)[\'"]', html_content, re.I)
        if site_key_match:
            params['site_key'] = site_key_match.group(1)
    
    elif captcha_type == CaptchaType.IMAGE:
        # Extract image URL
        img_match = re.search(r'<img[^>]*src=[\'"]([^\'"]*captcha[^\'"]*)[\'"]', html_content, re.I)
        if img_match:
            params['image_url'] = img_match.group(1)
    
    return params
