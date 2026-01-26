# Livestream Assets

This directory contains livestream episode banners, thumbnails, and promotional images.

## File Naming Convention

Files should follow the format: `s{season}-e{episode}-{type}.{ext}`

Where:
- `{season}` is the season number (e.g., 2, 3)
- `{episode}` is the episode number (e.g., 01, 02)
- `{type}` describes the image type (banner, thumbnail, social, etc.)
- `{ext}` is the file extension (jpg, png, etc.)

## Examples

- `s2-e01-banner.png` - Main episode banner
- `s3-e01-thumbnail.jpg` - Video thumbnail
- `s3-e02-social.png` - Social media promotional image

## Image Specifications

### Banners
- **Size**: 1920x1080px (16:9)
- **Format**: PNG or JPG
- **Max file size**: 2MB
- **Usage**: Episode headers, website banners

### Thumbnails
- **Size**: 1280x720px (16:9)
- **Format**: JPG
- **Max file size**: 500KB
- **Usage**: Video thumbnails, episode previews

### Social Media
- **Size**: 1200x630px (OG image)
- **Format**: PNG or JPG
- **Max file size**: 1MB
- **Usage**: Social media sharing

## Adding New Episode Images

1. Create images following the naming convention
2. Reference in `livestreams.json` if needed
3. Keep images optimized for web use
