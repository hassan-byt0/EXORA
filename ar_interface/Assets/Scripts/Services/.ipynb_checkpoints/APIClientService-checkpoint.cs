using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

public class APIClientService
{
    private string apiEndpoint;
    
    public APIClientService(string endpoint)
    {
        apiEndpoint = endpoint;
    }
    
    public IEnumerator ProcessImage(Texture2D image, System.Action<APIResponse> callback)
    {
        // Convert image to JPG
        byte[] imageBytes = image.EncodeToJPG();
        
        // Create form
        WWWForm form = new WWWForm();
        form.AddBinaryData("image", imageBytes, "capture.jpg", "image/jpeg");
        
        // Send request
        using (UnityWebRequest www = UnityWebRequest.Post(apiEndpoint, form))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                APIResponse response = JsonUtility.FromJson<APIResponse>(www.downloadHandler.text);
                callback?.Invoke(response);
            }
            else
            {
                callback?.Invoke(new APIResponse {
                    success = false,
                    errorMessage = www.error
                });
            }
        }
    }
    
    public IEnumerator ProcessAudio(AudioClip clip, System.Action<APIResponse> callback)
    {
        // Convert audio to WAV
        byte[] audioBytes = AudioUtils.AudioClipToWav(clip);
        
        // Create form
        WWWForm form = new WWWForm();
        form.AddBinaryData("audio", audioBytes, "recording.wav", "audio/wav");
        
        // Send request
        using (UnityWebRequest www = UnityWebRequest.Post(apiEndpoint, form))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                APIResponse response = JsonUtility.FromJson<APIResponse>(www.downloadHandler.text);
                callback?.Invoke(response);
            }
            else
            {
                callback?.Invoke(new APIResponse {
                    success = false,
                    errorMessage = www.error
                });
            }
        }
    }
    
    public IEnumerator ProcessText(string text, System.Action<APIResponse> callback)
    {
        // Create form
        WWWForm form = new WWWForm();
        form.AddField("text", text);
        
        // Send request
        using (UnityWebRequest www = UnityWebRequest.Post(apiEndpoint, form))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                APIResponse response = JsonUtility.FromJson<APIResponse>(www.downloadHandler.text);
                callback?.Invoke(response);
            }
            else
            {
                callback?.Invoke(new APIResponse {
                    success = false,
                    errorMessage = www.error
                });
            }
        }
    }
}

[System.Serializable]
public class APIResponse
{
    public bool success;
    public string message;
    public string audioClipPath;
    public string errorMessage;
}