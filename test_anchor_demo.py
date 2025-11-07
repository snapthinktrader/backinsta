"""
Test Script - Demonstrates Anchor Overlay on Sample Video
Creates a demo reel with anchor overlay
"""

import os
import sys
from anchor_overlay import AnchorOverlaySystem

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def create_demo_with_anchor():
    """Create a demo video with anchor overlay"""
    try:
        from moviepy import ImageClip, ColorClip, CompositeVideoClip
    except ImportError:
        from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
    
    print("\n🎬 Creating Demo Video with News Anchor Overlay")
    print("="*60)
    
    # Create a simple colored background video (30 seconds)
    print("📝 Creating base video (30s)...")
    base_video = ColorClip(size=(1080, 1920), color=(30, 30, 50), duration=30)
    
    # Initialize anchor system
    print("👩‍💼 Initializing Anchor Overlay System...")
    anchor_system = AnchorOverlaySystem()
    
    # Add anchor overlay
    print("🎨 Adding professional news anchor overlay...")
    final_video, anchor_name = anchor_system.add_to_video_clip(base_video, headline_height=180)
    
    # Export video
    output_path = "/Users/mahendrabahubali/Desktop/demo_with_anchor.mp4"
    print(f"💾 Exporting to: {output_path}")
    
    final_video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        logger=None,
        preset='fast'
    )
    
    print("\n✅ SUCCESS!")
    print(f"📺 Demo video created: {output_path}")
    print(f"👩‍💼 Anchor: {anchor_name}")
    print(f"🏢 Title: Senior News Reporter")
    print(f"📰 Organization: Forexyy Newsroom")
    print(f"🎤 Features: Voice speaker icon, LIVE indicator")
    
    # Clean up
    base_video.close()
    final_video.close()
    
    # Open the video
    print(f"\n🎬 Opening video...")
    os.system(f'open "{output_path}"')
    
    return True

if __name__ == "__main__":
    try:
        create_demo_with_anchor()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
