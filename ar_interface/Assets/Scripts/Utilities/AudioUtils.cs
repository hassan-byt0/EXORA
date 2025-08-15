using UnityEngine;
using System.IO;
using System;

public static class AudioUtils
{
    public static AudioClip CreateAudioClip(string name, float[] samples, int sampleRate)
    {
        AudioClip clip = AudioClip.Create(name, samples.Length, 1, sampleRate, false);
        clip.SetData(samples, 0);
        return clip;
    }
    
    public static byte[] AudioClipToWav(AudioClip clip)
    {
        using (MemoryStream stream = new MemoryStream())
        {
            using (BinaryWriter writer = new BinaryWriter(stream))
            {
                // Write WAV header
                writer.Write("RIFF".ToCharArray());
                writer.Write(36 + clip.samples * 2);
                writer.Write("WAVE".ToCharArray());
                
                // Write fmt chunk
                writer.Write("fmt ".ToCharArray());
                writer.Write(16);
                writer.Write((ushort)1); // PCM format
                writer.Write((ushort)clip.channels);
                writer.Write(clip.frequency);
                writer.Write(clip.frequency * clip.channels * 2); // byte rate
                writer.Write((ushort)(clip.channels * 2)); // block align
                writer.Write((ushort)16); // bits per sample
                
                // Write data chunk
                writer.Write("data".ToCharArray());
                writer.Write(clip.samples * clip.channels * 2);
                
                // Write audio data
                float[] samples = new float[clip.samples * clip.channels];
                clip.GetData(samples, 0);
                
                foreach (float sample in samples)
                {
                    short intSample = (short)(sample * short.MaxValue);
                    writer.Write(intSample);
                }
                
                return stream.ToArray();
            }
        }
    }
}