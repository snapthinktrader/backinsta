"""
Test script for Veo 3 lip-synced talking head video generation.
Generates a video of the anchor reading news commentary with precise lip sync.
"""

import os
import sys
import base64
import time
import json
from pathlib import Path
from google.cloud import aiplatform
from google.oauth2 import service_account
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Import Google TTS
from backinsta.google_tts_voice import GoogleTTSVoice

class VeoLipSyncGenerator:
    def __init__(self, project_id="nukkad-foods", location="us-central1"):
        """Initialize Veo video generator with lip sync support."""
        self.project_id = project_id
        self.location = location
        self.google_tts = GoogleTTSVoice()
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        print(f"✅ Initialized Veo generator for project: {project_id}")
    
    def encode_image_to_base64(self, image_path):
        """Convert image to base64 string."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_tts_audio(self, text, output_path):
        """Generate TTS audio from text."""
        print(f"\n🎤 Generating TTS audio...")
        print(f"Text: {text[:100]}...")
        
        self.google_tts.generate_voice(
            text=text,
            output_path=output_path,
            voice_name="en-US-Studio-O"  # Female news anchor voice
        )
        
        print(f"✅ Audio generated: {output_path}")
        return output_path
    
    def generate_lip_sync_video(self, anchor_image_path, narration_text, output_dir="test_output"):
        """
        Generate lip-synced talking head video using Veo 3.
        
        Args:
            anchor_image_path: Path to anchor face image
            narration_text: Text to be spoken by anchor
            output_dir: Directory to save output files
        
        Returns:
            Path to generated video file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*70)
        print("🎬 VEO 3 LIP-SYNC VIDEO GENERATION TEST")
        print("="*70)
        
        # Step 1: Generate TTS audio
        audio_path = os.path.join(output_dir, "narration_audio.mp3")
        self.generate_tts_audio(narration_text, audio_path)
        
        # Get audio duration
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(audio_path)
        audio_duration = len(audio) / 1000  # Convert to seconds
        print(f"📊 Audio duration: {audio_duration:.2f} seconds")
        
        # Step 2: Encode anchor image to base64
        print(f"\n🖼️  Loading anchor image: {anchor_image_path}")
        image_base64 = self.encode_image_to_base64(anchor_image_path)
        
        # Step 3: Create Veo 3 API request with lip sync
        print(f"\n🎯 Generating lip-synced video with Veo 3...")
        print(f"   Model: veo-3.0-generate-001")
        print(f"   Mode: Video + Audio (lip-synced)")
        print(f"   Duration: {min(8, int(audio_duration))} seconds")
        
        # Construct prompt for precise lip sync
        prompt = f"""
        A professional female news anchor speaking directly to camera.
        The anchor should have natural facial expressions and precise lip movements 
        synchronized with the voiceover audio.
        Clean professional studio background.
        High quality broadcast news presentation.
        The anchor is reading: "{narration_text[:100]}..."
        """.strip()
        
        # Prepare API endpoint
        endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-001:predictLongRunning"
        
        # Request payload
        request_data = {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": image_base64,
                    "mimeType": "image/jpeg"
                },
                "audioData": {
                    "bytesBase64Encoded": base64.b64encode(open(audio_path, 'rb').read()).decode('utf-8'),
                    "mimeType": "audio/mpeg"
                }
            }],
            "parameters": {
                "sampleCount": 1,
                "duration": min(8, int(audio_duration)),  # Max 8 seconds for Veo 3
                "aspectRatio": "9:16",  # Instagram Reels format
                "resizeMode": "crop",
                "lipSyncEnabled": True  # Enable precise lip synchronization
            }
        }
        
        print(f"\n📤 Sending request to Veo API...")
        print(f"   Aspect Ratio: 9:16 (Instagram Reels)")
        print(f"   Lip Sync: ENABLED")
        
        # Make request using Python requests and gcloud auth
        import subprocess
        import requests as req
        
        try:
            # Get access token from gcloud
            token_result = subprocess.run(
                ['gcloud', 'auth', 'print-access-token'],
                capture_output=True,
                text=True,
                check=True
            )
            access_token = token_result.stdout.strip()
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json; charset=utf-8'
            }
            
            response = req.post(endpoint, headers=headers, json=request_data, timeout=60)
            
            if response.status_code != 200:
                print(f"❌ API Error ({response.status_code}): {response.text}")
                return None
            
            response_data = response.json()
            operation_name = response_data.get('name')
            
            if not operation_name:
                print(f"❌ No operation name in response")
                print(f"Response: {response_data}")
                return None
            
            print(f"✅ Video generation started!")
            print(f"   Operation: {operation_name}")
            
            # Step 4: Poll for completion
            print(f"\n⏳ Waiting for video generation to complete...")
            print(f"   (This may take 2-5 minutes for high-quality lip sync)")
            
            operation_id = operation_name.split('/')[-1]
            max_attempts = 60  # 10 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                time.sleep(10)  # Check every 10 seconds
                
                # Check operation status
                status_endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-001:fetchPredictOperation"
                status_data = {"operationName": operation_name}
                
                status_response_http = req.post(status_endpoint, headers=headers, json=status_data, timeout=30)
                
                if status_response_http.status_code == 200:
                    status_response = status_response_http.json()
                    
                    if status_response.get('done'):
                        print(f"\n✅ Video generation complete!")
                        
                        # Debug: Print full response
                        print(f"\n📋 Full Response:")
                        print(json.dumps(status_response, indent=2))
                        
                        # Extract video data - try multiple response formats
                        video_bytes = None
                        
                        # Format 1: predictions array
                        predictions = status_response.get('response', {}).get('predictions', [])
                        if predictions and len(predictions) > 0:
                            video_data = predictions[0]
                            
                            if isinstance(video_data, dict):
                                # Check for videos array within predictions
                                if 'videos' in video_data and len(video_data['videos']) > 0:
                                    video_obj = video_data['videos'][0]
                                    if 'bytesBase64Encoded' in video_obj:
                                        video_bytes = base64.b64decode(video_obj['bytesBase64Encoded'])
                                        print(f"✅ Found video in predictions[0]['videos'][0]['bytesBase64Encoded']")
                                elif 'videoData' in video_data:
                                    video_bytes = base64.b64decode(video_data['videoData'])
                                    print(f"✅ Found video in 'videoData' field")
                                elif 'bytesBase64Encoded' in video_data:
                                    video_bytes = base64.b64decode(video_data['bytesBase64Encoded'])
                                    print(f"✅ Found video in 'bytesBase64Encoded' field")
                                elif 'gcsUri' in video_data:
                                    print(f"📦 Video stored in GCS: {video_data['gcsUri']}")
                                    return video_data['gcsUri']
                            elif isinstance(video_data, str):
                                video_bytes = base64.b64decode(video_data)
                                print(f"✅ Found video as base64 string")
                            
                            if video_bytes:
                                output_path = os.path.join(output_dir, "lip_sync_test.mp4")
                                
                                with open(output_path, 'wb') as f:
                                    f.write(video_bytes)
                                
                                file_size_mb = len(video_bytes) / (1024 * 1024)
                                print(f"\n🎉 SUCCESS!")
                                print(f"   Video saved: {output_path}")
                                print(f"   Size: {file_size_mb:.2f} MB")
                                print(f"   Duration: {audio_duration:.2f} seconds")
                                
                                return output_path
                        
                        print(f"❌ No video data in response")
                        return None
                    
                    else:
                        progress = (attempt / max_attempts) * 100
                        print(f"   [{attempt}/{max_attempts}] Still processing... {progress:.1f}%", end='\r')
                
            print(f"\n⚠️  Timeout waiting for video generation")
            return None
        
        except Exception as e:
            print(f"❌ Error making API request: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Test Veo 3 lip-sync video generation."""
    
    # Test text (short for quick testing)
    test_text = """
    Breaking news from the technology sector today. 
    Google has announced major advancements in artificial intelligence, 
    with their new video generation models showing unprecedented realism. 
    The company's Veo platform can now create highly detailed videos 
    with precise lip synchronization, marking a significant milestone 
    in AI-powered media creation.
    """
    
    # Anchor image path
    anchor_image = "/Users/mahendrabahubali/Desktop/QPost/WhatsApp Image 2025-10-25 at 07.04.58.jpeg"
    
    if not os.path.exists(anchor_image):
        print(f"❌ Anchor image not found: {anchor_image}")
        return
    
    # Initialize generator
    try:
        generator = VeoLipSyncGenerator()
        
        # Generate lip-synced video
        output_video = generator.generate_lip_sync_video(
            anchor_image_path=anchor_image,
            narration_text=test_text,
            output_dir="/Users/mahendrabahubali/Desktop/QPost/backinsta/test_output"
        )
        
        if output_video:
            print(f"\n{'='*70}")
            print(f"✅ TEST COMPLETE!")
            print(f"{'='*70}")
            print(f"\n📹 Generated video: {output_video}")
            print(f"\nTo view the video, run:")
            print(f"   open '{output_video}'")
            print(f"\nEstimated cost: ~$3-4 (based on Veo 3 pricing)")
        else:
            print(f"\n❌ Video generation failed")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
