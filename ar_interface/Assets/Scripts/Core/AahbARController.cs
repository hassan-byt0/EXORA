using UnityEngine;
using UnityEngine.XR.ARFoundation;

public class AahbARController : MonoBehaviour
{
    [Header("AR Components")]
    public ARSession arSession;
    public ARCameraManager arCamera;
    public ARAudioManager arAudio;
    
    [Header("UI Components")]
    public SpatialUIManager uiManager;
    public ARInputHandler inputHandler;
    
    [Header("Configuration")]
    public string apiEndpoint = "http://localhost:8000/api/v1/process";
    public float responseDisplayDistance = 1.5f;
    
    private APIClientService apiClient;
    private VoiceService voiceService;
    
    void Start()
    {
        // Initialize services
        apiClient = new APIClientService(apiEndpoint);
        voiceService = new VoiceService();
        
        // Setup event handlers
        inputHandler.OnImageCaptured += HandleImageCaptured;
        inputHandler.OnAudioCaptured += HandleAudioCaptured;
        inputHandler.OnTextSubmitted += HandleTextSubmitted;
        
        // Initialize AR session
        arSession.enabled = true;
        Debug.Log("AAHB AR Controller initialized");
    }
    
    private void HandleImageCaptured(Texture2D image)
    {
        Debug.Log("Processing captured image");
        StartCoroutine(apiClient.ProcessImage(image, HandleApiResponse));
    }
    
    private void HandleAudioCaptured(float[] samples, int sampleRate)
    {
        Debug.Log("Processing captured audio");
        AudioClip clip = AudioUtils.CreateAudioClip("UserAudio", samples, sampleRate);
        StartCoroutine(apiClient.ProcessAudio(clip, HandleApiResponse));
    }
    
    private void HandleTextSubmitted(string text)
    {
        Debug.Log("Processing text input: " + text);
        StartCoroutine(apiClient.ProcessText(text, HandleApiResponse));
    }
    
    private void HandleApiResponse(APIResponse response)
    {
        if (response.success)
        {
            // Display response in AR space
            Vector3 position = arCamera.transform.position + 
                              arCamera.transform.forward * responseDisplayDistance;
            uiManager.DisplayResponse(position, response);
            
            // Play audio response if available
            if (!string.IsNullOrEmpty(response.audioClipPath))
            {
                voiceService.PlaySpatialAudio(response.audioClipPath, position);
            }
        }
        else
        {
            uiManager.DisplayError(response.errorMessage);
        }
    }
    
    void Update()
    {
        // Handle gaze input
        if (inputHandler.IsGazingAtObject(out GameObject gazedObject))
        {
            uiManager.HighlightObject(gazedObject);
        }
        
        // Handle gesture input
        if (inputHandler.IsGesturePerformed(GestureType.Tap))
        {
            inputHandler.CaptureImage();
        }
    }
    
    void OnDestroy()
    {
        // Clean up resources
        inputHandler.OnImageCaptured -= HandleImageCaptured;
        inputHandler.OnAudioCaptured -= HandleAudioCaptured;
        inputHandler.OnTextSubmitted -= HandleTextSubmitted;
    }
}