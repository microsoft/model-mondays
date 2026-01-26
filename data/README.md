# Model Mondays Data Schema

This directory contains structured data files for the Model Mondays series. These JSON files serve as the single source of truth for episode metadata, speaker information, and event schedules.

## Table of Contents

- [Purpose](#purpose)
- [Assets Directory Structure](#assets-directory-structure)
- [Data Files](#data-files)
  - [speakers.json](#speakersjson)
  - [livestreams.json](#livestreamsjson)
  - [amas.json](#amasjson)
  - [seasons.json](#seasonsjson)
  - [topics.json](#topicsjson)
  - [resources.json](#resourcesjson)
  - [feedback.json](#feedbackjson)
- [Data Integrity Guidelines](#data-integrity-guidelines)
- [Usage Examples](#usage-examples)
  - [Finding all episodes featuring a specific speaker](#finding-all-episodes-featuring-a-specific-speaker)
  - [Generating upcoming schedule](#generating-upcoming-schedule)
  - [Building speaker profile with episode history](#building-speaker-profile-with-episode-history)
- [Additional Usage Examples](#additional-usage-examples)
  - [Finding resources by topic](#finding-resources-by-topic)
  - [Getting all feedback for an episode](#getting-all-feedback-for-an-episode)
  - [Finding most-referenced resources](#finding-most-referenced-resources)
- [Contributing](#contributing)
- [Future Enhancements](#future-enhancements)

## Purpose

The data files in this directory can be used to:
- Generate episode listings and calendars
- Build speaker profiles and bios
- Create automated announcements and recaps
- Drive website content and RSS feeds
- Support analytics and reporting
- Enable cross-referencing between episodes, speakers, and topics

## Assets Directory Structure

The `assets/` subdirectory contains all images and media files referenced in the data files:

- **`assets/people/`** - Speaker profile images and headshots
  - Format: `{speaker-id}.jpg` or `{speaker-id}.png`
  - Example: `nitya-narasimhan.jpg`

- **`assets/livestream/`** - Livestream episode banners, thumbnails, and promotional images
  - Format: `s{season}-e{episode}-{type}.{ext}`
  - Example: `s2-e01-banner.png`, `s3-e01-thumbnail.jpg`

- **`assets/ama/`** - AMA session banners and promotional images
  - Format: `s{season}-ama{episode}-{type}.{ext}`
  - Example: `s2-ama01-banner.png`

- **`assets/misc/`** - Season banners, logos, and other shared assets
  - Season banners: `season-{number}-banner.png`
  - Example: `season-3-banner.png`

All image paths in JSON files are relative to the `data/` directory.

## Data Files

### `speakers.json`
Contains information about all hosts, co-hosts, guests, and speakers who have appeared in the series.

**Schema:**
```json
{
  "id": "string (unique identifier, e.g., 'nitya-narasimhan')",
  "name": "string (full name)",
  "role": "string (job title)",
  "affiliation": "string (company/organization)",
  "profileImage": "string (path relative to data/, e.g., 'assets/people/speaker-id.jpg')",
  "bio": "string (short biography)",
  "socialLinks": {
    "linkedin": "string (URL)",
    "twitter": "string (URL)",
    "github": "string (URL)",
    "website": "string (URL)"
  },
  "expertise": ["array of strings (areas of expertise)"]
}
```

### `livestreams.json`
Contains metadata for all Model Mondays livestream episodes (broadcast on Mondays).

**Schema:**
```json
{
  "id": "string (unique identifier, e.g., 's2-e01')",
  "season": "number",
  "episode": "number",
  "title": "string (episode title)",
  "description": "string (episode description)",
  "date": "string (ISO 8601 date)",
  "time": "string (time in ET, e.g., '1:30pm ET')",
  "duration": "number (minutes)",
  "status": "string (scheduled|completed|cancelled)",
  "host": "string (speaker ID reference)",
  "spotlight": {
    "title": "string (tech spotlight title)",
    "description": "string (spotlight description)",
    "speakers": ["array of strings (speaker ID references)"],
    "resources": [
      {
        "title": "string",
        "url": "string",
        "type": "string (documentation|lab|blog|video|repo)"
      }
    ]
  },
  "customerStory": {
    "title": "string (customer story title)",
    "company": "string (company name)",
    "speakers": ["array of strings (speaker ID references)"],
    "description": "string"
  },
  "highlights": [
    {
      "title": "string (news item title)",
      "url": "string",
      "description": "string"
    }
  ],
  "studyCorner": {
    "lesson": "string (e.g., 'L1: Language Models')",
    "description": "string",
    "resources": [
      {
        "title": "string",
        "url": "string"
      }
    ]
  },
  "links": {
    "registration": "string (URL)",
    "recording": "string (URL)",
    "recap": "string (path to recap document)",
    "announcement": "string (path to announcement document)",
    "summary": "string (path to summary document)"
  },
  "tags": ["array of strings (topics/keywords)"]
}
```

### `amas.json`
Contains metadata for all Foundry Friday AMA sessions (broadcast on Fridays).

**Schema:**
```json
{
  "id": "string (unique identifier, e.g., 's2-ama01')",
  "season": "number",
  "episode": "number (corresponds to livestream episode)",
  "title": "string (AMA title)",
  "description": "string (AMA description)",
  "date": "string (ISO 8601 date)",
  "time": "string (time in ET, e.g., '1:30pm ET')",
  "duration": "number (minutes)",
  "status": "string (scheduled|completed|cancelled)",
  "host": "string (speaker ID reference)",
  "guests": ["array of strings (speaker ID references)"],
  "topics": ["array of strings (discussion topics)"],
  "links": {
    "registration": "string (Discord event URL)",
    "recap": "string (path to recap document)",
    "announcement": "string (path to announcement document)"
  },
  "relatedLivestreamId": "string (livestream episode ID)",
  "resources": [
    {
      "title": "string",
      "url": "string",
      "type": "string (documentation|lab|blog|video|repo)"
    }
  ],
  "keyTakeaways": ["array of strings"],
  "tags": ["array of strings (topics/keywords)"]
}
```

### `seasons.json`
Contains high-level information about each season of the series.

**Schema:**
```json
{
  "season": "number",
  "title": "string (season title)",
  "startDate": "string (ISO 8601 date)",
  "endDate": "string (ISO 8601 date)",
  "theme": "string (season theme/focus)",
  "description": "string (season description)",
  "totalEpisodes": "number",
  "totalAMAs": "number",
  "status": "string (planned|active|completed)",
  "banner": "string (path relative to data/, e.g., 'assets/misc/season-3-banner.png')"
}
```

### `topics.json`
Contains a taxonomy of topics covered across all episodes, enabling topic-based navigation and filtering.

**Schema:**
```json
{
  "id": "string (unique identifier, e.g., 'reasoning-models')",
  "name": "string (topic name)",
  "category": "string (model-types|techniques|platforms|tools|practices)",
  "description": "string (topic description)",
  "relatedTopics": ["array of strings (topic IDs)"],
  "episodes": ["array of strings (episode IDs that cover this topic)"],
  "resources": ["array of strings (resource IDs)"],
  "tags": ["array of strings (keywords)"]
}
```

### `resources.json`
Central repository of all shared resources (documentation, labs, blogs, videos, repos) referenced across episodes.

**Schema:**
```json
{
  "id": "string (unique identifier, e.g., 'azure-ai-foundry-reasoning-docs')",
  "title": "string (resource title)",
  "url": "string (resource URL)",
  "type": "string (documentation|lab|blog|video|repo|tool|course)",
  "description": "string (resource description)",
  "provider": "string (Microsoft|GitHub|External)",
  "topics": ["array of strings (topic IDs)"],
  "episodes": ["array of strings (episode IDs that reference this)"],
  "dateAdded": "string (ISO 8601 date)",
  "featured": "boolean (whether to highlight this resource)"
}
```

### `feedback.json`
Community feedback, questions, and discussions from livestreams and AMA sessions.

**Schema:**
```json
{
  "id": "string (unique identifier, e.g., 'fb-s2e01-001')",
  "episodeId": "string (livestream or AMA ID)",
  "type": "string (question|comment|suggestion|issue)",
  "content": "string (feedback content)",
  "author": "string (community member name or anonymous)",
  "timestamp": "string (ISO 8601 datetime)",
  "status": "string (pending|answered|resolved|archived)",
  "response": "string (response to feedback, if any)",
  "tags": ["array of strings (keywords)"],
  "upvotes": "number (community engagement metric)"
}
```

## Data Integrity Guidelines

1. **IDs**: Use lowercase with hyphens (kebab-case) for all IDs
2. **Dates**: Use ISO 8601 format (YYYY-MM-DD) for consistency
3. **References**: Use speaker IDs to reference speakers (enables reusability)
4. **Paths**: Use relative paths from repository root for all files
5. **URLs**: Include full URLs with protocol (https://)
6. **Status**: Update status fields as episodes progress
7. **Arrays**: Keep arrays empty `[]` rather than null for consistency

## Usage Examples

### Finding all episodes featuring a specific speaker
```javascript
const speakerId = 'marlene-mhangami';
const episodes = livestreams.filter(ep => 
  ep.host === speakerId || 
  ep.spotlight?.speakers.includes(speakerId)
);
```

### Generating upcoming schedule
```javascript
const now = new Date();
const upcoming = livestreams
  .filter(ep => new Date(ep.date) >= now && ep.status === 'scheduled')
  .sort((a, b) => new Date(a.date) - new Date(b.date));
```

### Building speaker profile with episode history
```javascript
const speakerId = 'nitya-narasimhan';
const speaker = speakers.find(s => s.id === speakerId);
const appearances = livestreams.filter(ep => 
  ep.host === speakerId || 
  ep.spotlight?.speakers.includes(speakerId) ||
  ep.customerStory?.speakers.includes(speakerId)
);
```

## Contributing

When adding new episodes or speakers:
1. Follow the schema definitions exactly
2. Validate JSON syntax before committing
3. Use consistent formatting (2-space indentation)
4. Update cross-references between related data files
5. Ensure all referenced IDs exist in their respective files

## Additional Usage Examples

### Finding resources by topic
```javascript
const topicId = 'reasoning-models';
const topic = topics.find(t => t.id === topicId);
const relatedResources = resources.filter(r => r.topics.includes(topicId));
const relatedEpisodes = livestreams.filter(ep => topic.episodes.includes(ep.id));
```

### Getting all feedback for an episode
```javascript
const episodeId = 's2-e01';
const episodeFeedback = feedback
  .filter(f => f.episodeId === episodeId)
  .sort((a, b) => b.upvotes - a.upvotes);
```

### Finding most-referenced resources
```javascript
const popularResources = resources
  .sort((a, b) => b.episodes.length - a.episodes.length)
  .slice(0, 10);
```

## Future Enhancements

Potential additions to the schema:
- `partners.json` - Information about partner organizations
- `metrics.json` - Viewership and engagement data
- `events.json` - Conference appearances and special events
