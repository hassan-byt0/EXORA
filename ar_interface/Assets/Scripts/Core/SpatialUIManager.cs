using UnityEngine;
using TMPro;
using UnityEngine.XR.ARFoundation;

public class SpatialUIManager : MonoBehaviour
{
    [Header("UI Prefabs")]
    public GameObject responsePrefab;
    public GameObject errorPrefab;
    public GameObject loadingIndicator;
    
    [Header("Configuration")]
    public float uiFadeDuration = 1.0f;
    public float maxViewAngle = 30f;
    
    private GameObject currentResponse;
    private CanvasGroup currentResponseCanvas;
    private ARCameraManager arCamera;
    
    void Start()
    {
        arCamera = FindObjectOfType<ARCameraManager>();
        loadingIndicator.SetActive(false);
    }
    
    public void DisplayResponse(Vector3 position, APIResponse response)
    {
        // Remove previous response
        ClearCurrentResponse();
        
        // Create new response object
        currentResponse = Instantiate(responsePrefab, position, Quaternion.identity);
        currentResponseCanvas = currentResponse.GetComponent<CanvasGroup>();
        
        // Set response content
        TextMeshProUGUI textComponent = currentResponse.GetComponentInChildren<TextMeshProUGUI>();
        if (textComponent != null)
        {
            textComponent.text = response.message;
        }
        
        // Align with camera
        AlignWithCamera(currentResponse.transform);
        
        // Fade in
        StartCoroutine(FadeUI(currentResponseCanvas, 0f, 1f, uiFadeDuration));
        
        // Start tracking position
        StartCoroutine(UpdateUIPosition());
    }
    
    public void DisplayError(string errorMessage)
    {
        Vector3 position = arCamera.transform.position + 
                          arCamera.transform.forward * 1f;
        
        // Create error object
        GameObject errorObj = Instantiate(errorPrefab, position, Quaternion.identity);
        CanvasGroup canvasGroup = errorObj.GetComponent<CanvasGroup>();
        
        // Set error message
        TextMeshProUGUI textComponent = errorObj.GetComponentInChildren<TextMeshProUGUI>();
        if (textComponent != null)
        {
            textComponent.text = "Error: " + errorMessage;
        }
        
        // Align with camera
        AlignWithCamera(errorObj.transform);
        
        // Fade in and out
        StartCoroutine(FadeUI(canvasGroup, 0f, 1f, uiFadeDuration, () => {
            StartCoroutine(FadeUI(canvasGroup, 1f, 0f, uiFadeDuration * 2, () => {
                Destroy(errorObj);
            }));
        });
    }
    
    public void ShowLoadingIndicator(bool show)
    {
        loadingIndicator.SetActive(show);
        if (show)
        {
            loadingIndicator.transform.position = arCamera.transform.position + 
                                                arCamera.transform.forward * 1f;
            AlignWithCamera(loadingIndicator.transform);
        }
    }
    
    public void HighlightObject(GameObject obj)
    {
        // Implementation for highlighting objects
        // Could use outline effect, color change, etc.
    }
    
    private void AlignWithCamera(Transform uiTransform)
    {
        // Make UI face camera with a slight offset for readability
        Vector3 directionToCamera = arCamera.transform.position - uiTransform.position;
        directionToCamera.y = 0; // Keep upright
        Quaternion targetRotation = Quaternion.LookRotation(directionToCamera);
        uiTransform.rotation = targetRotation;
    }
    
    private System.Collections.IEnumerator UpdateUIPosition()
    {
        while (currentResponse != null)
        {
            // Check if UI is within view
            Vector3 directionToUI = currentResponse.transform.position - arCamera.transform.position;
            float angle = Vector3.Angle(arCamera.transform.forward, directionToUI);
            
            if (angle > maxViewAngle)
            {
                // Reposition UI to be in view
                Vector3 newPosition = arCamera.transform.position + 
                                     arCamera.transform.forward * responseDisplayDistance;
                currentResponse.transform.position = Vector3.Lerp(
                    currentResponse.transform.position, 
                    newPosition, 
                    Time.deltaTime * 2f
                );
                AlignWithCamera(currentResponse.transform);
            }
            
            yield return null;
        }
    }
    
    private System.Collections.IEnumerator FadeUI(
        CanvasGroup canvasGroup, 
        float startAlpha, 
        float endAlpha, 
        float duration,
        System.Action onComplete = null
    ) {
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            canvasGroup.alpha = Mathf.Lerp(startAlpha, endAlpha, elapsed / duration);
            elapsed += Time.deltaTime;
            yield return null;
        }
        
        canvasGroup.alpha = endAlpha;
        onComplete?.Invoke();
    }
    
    public void ClearCurrentResponse()
    {
        if (currentResponse != null)
        {
            Destroy(currentResponse);
            currentResponse = null;
        }
    }
}