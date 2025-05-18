import requests
import json
from .logger_srv import log_info, log_exception
from urllib.parse import urljoin

def get_foundation_model(aicore_credentials, prompt):
    """
    Get response from SAP AI Core foundation model with a prompt
    """
    try:
        log_info("[AICore] Starting foundation model inference request")
        # Extract and validate AI Core credentials
        base_url = aicore_credentials.get('url', '')
        if not base_url:
            log_exception("[AICore] AI Core base URL not found in credentials", Exception("No URL"))
            raise Exception("AI Core base URL not found in credentials")
        log_info(f"[AICore] Using base_url: {base_url}")
        # Ensure base_url ends with /
        if not base_url.endswith('/'):
            base_url += '/'
        # Construct API URLs
        deployment_url = urljoin(base_url, 'api/v1/inference/deployments')
        log_info(f"[AICore] Deployment URL: {deployment_url}")
        # Get token from credentials
        token = aicore_credentials.get('token')
        if not token:
            log_exception("[AICore] No token found in AI Core credentials", Exception("No Token"))
            raise Exception("No token found in AI Core credentials")
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        log_info(f"[AICore] Requesting deployments from: {deployment_url}")
        # Get available deployments
        deployments_response = requests.get(
            deployment_url,
            headers=headers,
            verify=True  # Enable SSL verification
        )
        log_info(f"[AICore] Deployments response status: {deployments_response.status_code}")
        if deployments_response.status_code != 200:
            log_exception(f"[AICore] Failed to get deployments: {deployments_response.text}", Exception("Deployments Error"))
            raise Exception(f"Failed to get deployments: {deployments_response.text}")
        deployments = deployments_response.json()
        log_info(f"[AICore] Available deployments: {json.dumps(deployments, indent=2)[:1000]}")
        # Find foundation model deployment
        foundation_deployment = next(
            (d for d in deployments.get('deployments', []) 
             if 'foundation' in d.get('name', '').lower()),
            None
        )
        if not foundation_deployment:
            log_exception("[AICore] No foundation model deployment found", Exception("No Foundation Deployment"))
            raise Exception("No foundation model deployment found. Available deployments: " + 
                          ", ".join([d.get('name', 'unnamed') for d in deployments.get('deployments', [])]))
        deployment_id = foundation_deployment['id']
        log_info(f"[AICore] Found foundation model deployment: {deployment_id}")
        # Prepare inference request
        inference_url = f"{deployment_url}/{deployment_id}/inferenceendpoint"
        payload = {
            "inputs": [prompt]  # Ensure prompt is wrapped in a list
        }
        log_info(f"[AICore] Making inference request to: {inference_url} with payload: {payload}")
        # Make inference request
        inference_response = requests.post(
            inference_url,
            headers=headers,
            json=payload,
            verify=True  # Enable SSL verification
        )
        log_info(f"[AICore] Inference response status: {inference_response.status_code}")
        if inference_response.status_code != 200:
            log_exception(f"[AICore] Inference failed: {inference_response.text}", Exception("Inference Error"))
            raise Exception(f"Inference failed: {inference_response.text}")
        log_info(f"[AICore] Inference response: {inference_response.text[:1000]}")
        return inference_response.json()
    except Exception as e:
        log_exception("[AICore] Error testing foundation model", e)
        raise e
