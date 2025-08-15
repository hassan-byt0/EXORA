using UnityEngine;

public class VoiceService
{
    private AudioSource audioSource;
    private float spatialBlend = 1.0f; // Fully spatialized
    
    public VoiceService()
    {
        // Create audio source object
        GameObject audioObject = new GameObject("VoiceService");
        audioSource = audioObject.AddComponent<AudioSource>();
        audioSource.spatialBlend = spatialBlend;
    }
    
    public void PlaySpatialAudio(string clipPath, Vector3 position)
    {
        // Load audio clip
        AudioClip clip = Resources.Load<AudioClip>(clipPath);
        if (clip == null)
        {
            Debug.LogError($"Audio clip not found: {clipPath}");
            return;
        }
        
        // Position audio source
        audioSource.transform.position = position;
        
        // Play audio
        audioSource.PlayOneShot(clip);
        Debug.Log($"Playing spatial audio at {position}");
    }
    
    public void SetSpatialBlend(float blend)
    {
        spatialBlend = Mathf.Clamp01(blend);
        audioSource.spatialBlend = spatialBlend;
    }
}