# Caption & Description Format

## Instagram Reel Caption Format

```
[AI-Generated Analysis from Groq]

#news #breakingnews #[section] #instagram #reels #viral #trending #fyp #foryou #explore

📰 Follow @usdaily24 for daily news
🌐 forexyy.com
```

**Example:**
```
Breaking news in the tech world! This development could reshape how we think about artificial intelligence and automation. Industry experts are weighing in on the potential implications for businesses and consumers alike.

#news #breakingnews #technology #instagram #reels #viral #trending #fyp #foryou #explore

📰 Follow @usdaily24 for daily news
🌐 forexyy.com
```

## YouTube Shorts Description Format

```
[AI-Generated Analysis from Groq]

🌐 forexyy.com - Your Daily News Source

#Shorts #News #BreakingNews #[Section]
```

**Example:**
```
Breaking news in the tech world! This development could reshape how we think about artificial intelligence and automation. Industry experts are weighing in on the potential implications for businesses and consumers alike.

🌐 forexyy.com - Your Daily News Source

#Shorts #News #BreakingNews #technology
```

## AI Analysis Generation

The AI analysis is generated using **Groq API** with the `llama-3.1-8b-instant` model.

**Prompt:**
```
Analyze this news article and provide a concise, engaging summary in 2-3 sentences. 
Focus on the key facts and why it matters. Write in a journalistic style suitable for 
social media.

Title: [Article Title]
Abstract: [Article Abstract]
```

**Parameters:**
- Model: `llama-3.1-8b-instant`
- Max tokens: 150
- Temperature: 0.7

## Branding Guidelines

### Instagram
- Account: **@usdaily24**
- Always include account mention in caption
- Use website URL: **forexyy.com**
- Logo watermark: Top-right corner, 15% of image width

### YouTube
- Channel: **forexyynewsletter@gmail.com**
- Branding line: **"🌐 forexyy.com - Your Daily News Source"**
- Always include #Shorts hashtag for proper categorization

## Hashtag Strategy

### Instagram (High engagement)
- #news #breakingnews
- #[section] (specific to article category)
- #instagram #reels #viral #trending
- #fyp #foryou #explore (algorithm tags)

### YouTube (SEO focused)
- #Shorts (REQUIRED for Shorts feed)
- #News #BreakingNews
- #[Section] (technology, business, politics, etc.)

## Content Flow

1. **Fetch article** from NYT API
2. **Generate AI analysis** using Groq
3. **Create overlay** with transparent text + logo
4. **Convert to video** (7 seconds, 1080x1920, static)
5. **Post to Instagram** with full caption format
6. **Post to YouTube** with AI analysis + branding
7. **Track in MongoDB** with lightweight storage

## Why This Format?

- **AI Analysis**: More engaging than raw abstracts, written in social media style
- **Branding**: Consistent forexyy.com presence across platforms
- **Hashtags**: Platform-specific optimization (engagement vs SEO)
- **Concise**: Fits platform character limits and user attention spans
- **Professional**: Maintains journalistic credibility while being accessible
