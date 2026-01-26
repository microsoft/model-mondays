# People Assets

This directory contains speaker profile images and headshots.

## File Naming Convention

Files should follow the format: `{speaker-id}.{ext}`

Where:
- `{speaker-id}` matches the speaker's ID in `speakers.json`
- `{ext}` is the file extension (jpg, png, etc.)

## Examples

- `nitya-narasimhan.jpg`
- `marlene-mhangami.png`
- `sanjeev-jagtap.jpg`

## Image Specifications

- **Recommended size**: 400x400px (square)
- **Format**: JPG or PNG
- **Max file size**: 500KB
- **Style**: Professional headshots with neutral background

## Adding New Speaker Images

1. Save the image with the speaker's ID as the filename
2. Update the `profileImage` field in `speakers.json` to reference the file
3. Format: `"profileImage": "assets/people/{speaker-id}.jpg"`
