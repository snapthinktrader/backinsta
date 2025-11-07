# News Anchor Overlay Feature

## Overview
The animated reel system now includes a **professional news anchor overlay** that appears in the top-right corner of every reel, making it look like a professional newsroom broadcast.

## Features

### 🎬 Visual Components
1. **Anchor Photo**: Circular headshot with white border
2. **Unique Name**: Randomly selected US-based female name
3. **Title**: "Senior News Reporter"
4. **Organization**: "Forexyy Newsroom"
5. **Voice Speaker Icon**: Animated speaker symbol
6. **LIVE Indicator**: Red "LIVE" badge

### 📍 Positioning
- **Location**: Top-right corner of video
- **Height**: Matches headline text area (~180px)
- **Width**: Proportional to height (maintains aspect ratio)
- **Duration**: Appears throughout entire video

## Anchor Names
The system randomly selects from a pool of professional US-based female names:
- Sarah Mitchell
- Jessica Thompson
- Emily Rodriguez
- Rachel Anderson
- Amanda Williams
- Lauren Davis
- Michelle Carter
- Jennifer Martinez
- Ashley Taylor
- Samantha Brooks
- Nicole Patterson
- Christina Hayes
- Melissa Cooper
- Rebecca Morgan
- Stephanie Collins

**Each reel gets a unique anchor name** to maintain variety.

## Implementation

### Files Created
1. **`anchor_overlay.py`**: Core anchor overlay system
   - `AnchorOverlaySystem` class
   - Name generation
   - Overlay composition
   - Video integration

2. **Integration in `animated_reel_creator.py`**:
   - Imported `AnchorOverlaySystem`
   - Added overlay after headline text
   - Applied to entire video duration

### Usage Example

```python
from anchor_overlay import AnchorOverlaySystem

# Create anchor system
anchor_system = AnchorOverlaySystem()

# Add to video clip
final_video, anchor_name = anchor_system.add_to_video_clip(
    video_clip,
    headline_height=180
)

print(f"✅ Added anchor: {anchor_name}")
# Output: ✅ Added anchor: Sarah Mitchell
```

## Reference Image
The anchor photo is loaded from:
```
/Users/mahendrabahubali/Desktop/QPost/WhatsApp Image 2025-10-25 at 07.04.58.jpeg
```

This image is:
- Resized to match headline height
- Converted to circular/rounded shape
- Given a white border for professional look
- Positioned in top-right corner

## Design Specifications

### Layout
```
┌────────────────────────────────────────────┐
│  HEADLINE TEXT HERE           ┌──────────┐ │
│                               │  ANCHOR  │ │
│                               │   PHOTO  │ │
│                               │          │ │
│                               │  Name    │ │
│                               │  Title   │ │
│                               │  Org     │ │
│                               │  🔊 LIVE │ │
│                               └──────────┘ │
│                                            │
│         VIDEO CONTENT HERE                 │
│                                            │
└────────────────────────────────────────────┘
```

### Colors
- **Background**: Semi-transparent black (opacity: 70%)
- **Name Text**: White (#FFFFFF)
- **Title Text**: Gold (#FFD700)
- **Organization**: Light Gray (#CCCCCC)
- **LIVE Badge**: Red background (#FF0000)
- **Anchor Border**: White (#FFFFFF)

### Typography
- **Name**: Arial Bold, 32px
- **Title**: Arial, 22px
- **Organization**: Arial, 20px
- **LIVE**: Arial Bold, 16px

## Testing

### Test the Overlay System
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
python3 anchor_overlay.py
```

This will:
1. Generate 5 unique anchor names
2. Create a test overlay image
3. Save to Desktop: `test_anchor_overlay.png`

### Create Demo Video
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
python3 -c "
from anchor_overlay import AnchorOverlaySystem
from moviepy import ColorClip
anchor = AnchorOverlaySystem()
video = ColorClip(size=(1080, 1920), color=(30, 30, 50), duration=5)
final, name = anchor.add_to_video_clip(video, headline_height=180)
final.write_videofile('/Users/mahendrabahubali/Desktop/anchor_demo.mp4', fps=30)
"
```

## Integration with Animated Reels

### Workflow
1. **Create base video** (NYT image + stock footage)
2. **Add headline text overlay** (throughout video)
3. **Add anchor overlay** ← NEW STEP
4. **Add voice narration** (Google TTS)
5. **Add synced captions** (word-by-word)
6. **Export final video**

### When It Appears
The anchor overlay is added in `animated_reel_creator.py` at **Step 6b**:

```python
# Step 6b: Add professional news anchor overlay (top right corner)
logger.info("👩‍💼 Adding professional news anchor overlay...")
try:
    final_video, anchor_name = self.anchor_system.add_to_video_clip(
        final_video, 
        headline_height=180
    )
    logger.info(f"✅ Added anchor: {anchor_name} - Senior News Reporter, Forexyy Newsroom")
except Exception as anchor_error:
    logger.warning(f"⚠️ Could not add anchor overlay: {anchor_error}")
```

## Customization

### Change Anchor Photo
Replace the image at:
```
/Users/mahendrabahubali/Desktop/QPost/WhatsApp Image 2025-10-25 at 07.04.58.jpeg
```

### Add More Names
Edit `FEMALE_ANCHOR_NAMES` list in `anchor_overlay.py`:
```python
FEMALE_ANCHOR_NAMES = [
    "Sarah Mitchell",
    "Your Custom Name",  # Add here
    # ... more names
]
```

### Adjust Position
Modify `add_to_video_clip()` method in `anchor_overlay.py`:
```python
# Position in top-right corner
x_position = video_width - overlay_width - 20  # Change offset
y_position = 20  # Change vertical position
```

### Change Title/Organization
Edit `create_anchor_overlay()` method:
```python
# Draw title
draw.text((35, 65), "Your Custom Title", font=subtitle_font, fill='#FFD700')

# Draw organization
draw.text((35, 95), "Your Organization", font=org_font, fill='#CCCCCC')
```

## Dual System Architecture

### Static Reels (Original)
- **File**: `generate_reels_local.py`
- **Features**: Static image + voice
- **Status**: ✅ Working, DO NOT MODIFY
- **No anchor overlay** (keeps original simple design)

### Animated Reels (New)
- **File**: `generate_animated_reels.py`
- **Features**: NYT image + stock footage + voice + captions + **anchor overlay**
- **Status**: ✅ Active development
- **Includes anchor overlay** (professional broadcast look)

## Benefits

### Professional Appearance
- Makes reels look like professional news broadcasts
- Adds credibility and authority
- Consistent branding with "Forexyy Newsroom"

### Engagement
- Human element increases viewer connection
- "LIVE" badge creates urgency
- Voice icon indicates audio content

### Brand Recognition
- Consistent anchor presentation
- Unique name per reel maintains variety
- Professional title establishes expertise

## Troubleshooting

### Anchor Photo Not Loading
```
⚠️ Could not load anchor image: [error]
```
**Solution**: Check that WhatsApp image exists at correct path

### Overlay Not Appearing
```
⚠️ Could not add anchor overlay: [error]
```
**Solution**: Verify moviepy is installed and video clip is valid

### Name Collision
If all 15 names are used, the system automatically resets the pool.

## Examples

### Test Output
```
🎬 Testing Anchor Overlay System

📝 Testing unique name generation:
   1. Nicole Patterson
   2. Jessica Thompson
   3. Jennifer Martinez
   4. Stephanie Collins
   5. Sarah Mitchell

🎨 Creating anchor overlay image...
✅ Created overlay for: Rachel Anderson
   Size: (450, 200)
💾 Saved test overlay to: /Users/mahendrabahubali/Desktop/test_anchor_overlay.png
```

### Video Creation Output
```
✅ Added anchor overlay: Sarah Mitchell
✅ Added anchor: Sarah Mitchell - Senior News Reporter, Forexyy Newsroom
```

## Next Steps

1. ✅ Anchor overlay system created
2. ✅ Integrated into animated reel creator
3. ✅ Test demo video created
4. ⏳ Generate full animated reel with real NYT article
5. ⏳ Deploy to production (Render)

## Notes

- The anchor overlay uses the same height as the headline text for visual consistency
- The overlay is semi-transparent to not completely block the video content
- The circular anchor photo with white border creates a professional look
- The "LIVE" badge and voice icon add dynamic elements
- Each reel gets a unique anchor name for variety while maintaining consistent branding
