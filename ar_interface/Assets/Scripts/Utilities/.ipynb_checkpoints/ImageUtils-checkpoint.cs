using UnityEngine;
using UnityEngine.XR.ARSubsystems;

public static class ImageUtils
{
    public static Texture2D ConvertToTexture2D(XRCpuImage cpuImage)
    {
        // Create texture parameters
        XRCpuImage.ConversionParams conversionParams = new XRCpuImage.ConversionParams
        {
            inputRect = new RectInt(0, 0, cpuImage.width, cpuImage.height),
            outputDimensions = new Vector2Int(cpuImage.width, cpuImage.height),
            outputFormat = TextureFormat.RGBA32,
            transformation = XRCpuImage.Transformation.MirrorY
        };
        
        // Create texture
        Texture2D texture = new Texture2D(
            conversionParams.outputDimensions.x,
            conversionParams.outputDimensions.y,
            conversionParams.outputFormat,
            false
        );
        
        // Convert image
        cpuImage.Convert(conversionParams, texture.GetRawTextureData<byte>());
        texture.Apply();
        
        return texture;
    }
    
    public static byte[] TextureToJpg(Texture2D texture, int quality = 75)
    {
        return texture.EncodeToJPG(quality);
    }
}