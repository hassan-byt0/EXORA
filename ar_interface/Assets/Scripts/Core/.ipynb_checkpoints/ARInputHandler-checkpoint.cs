using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.InputSystem;

public class ARInputHandler : MonoBehaviour
{
    [Header("Input Settings")]
    public float gazeMaxDistance = 10f;
    public LayerMask interactableLayers;
    
    [Header("Gesture Settings")]
    public float tapDurationThreshold = 0.2f;
    
    // Events
    public delegate void ImageCapturedHandler(Texture2D image);
    public event ImageCapturedHandler OnImageCaptured;
    
    public delegate void AudioCapturedHandler(float[] samples, int sampleRate);
    public event AudioCapturedHandler OnAudioCaptured;
    
    public delegate void TextSubmittedHandler(string text);
    public event TextSubmittedHandler OnTextSubmitted;
    
    // Internal state
    private ARCameraManager arCamera;
    private float tapStartTime;
    private bool isTapping;
    
    void Start()
    {
        arCamera = FindObjectOfType<ARCameraManager>();
        
        // Setup input actions
        var inputActions = new InputActions();
        inputActions.Enable();
        
        inputActions.AR.Tap.started += ctx => StartTap();
        inputActions.AR.Tap.canceled += ctx => EndTap();
        inputActions.AR.Voice.started += ctx => StartVoiceCapture();
        inputActions.AR.Voice.canceled += ctx => EndVoiceCapture();
    }
    
    public void CaptureImage()
    {
        if (arCamera.TryAcquireLatestCpuImage(out XRCpuImage image))
        {
            // Convert to Texture2D
            Texture2D texture = ImageUtils.ConvertToTexture2D(image);
            OnImageCaptured?.Invoke(texture);
        }
    }
    
    public void StartVoiceCapture()
    {
        Debug.Log("Voice capture started");
        ARAudioManager.Instance.StartRecording();
    }
    
    public void EndVoiceCapture()
    {
        Debug.Log("Voice capture ended");
        ARAudioManager.Instance.StopRecording((samples, sampleRate) => {
            OnAudioCaptured?.Invoke(samples, sampleRate);
        });
    }
    
    public void SubmitText(string text)
    {
        OnTextSubmitted?.Invoke(text);
    }
    
    public bool IsGazingAtObject(out GameObject gazedObject)
    {
        Ray ray = new Ray(arCamera.transform.position, arCamera.transform.forward);
        if (Physics.Raycast(ray, out RaycastHit hit, gazeMaxDistance, interactableLayers))
        {
            gazedObject = hit.collider.gameObject;
            return true;
        }
        
        gazedObject = null;
        return false;
    }
    
    public bool IsGesturePerformed(GestureType gestureType)
    {
        switch (gestureType)
        {
            case GestureType.Tap:
                return isTapping && (Time.time - tapStartTime) < tapDurationThreshold;
            default:
                return false;
        }
    }
    
    private void StartTap()
    {
        tapStartTime = Time.time;
        isTapping = true;
    }
    
    private void EndTap()
    {
        isTapping = false;
    }
}

public enum GestureType
{
    Tap,
    Swipe,
    Pinch
}