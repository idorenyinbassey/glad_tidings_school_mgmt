# Carousel Images Management

## Current Setup

The landing page carousel uses reliable external image URLs with fallback placeholders to ensure images always display properly.

## Image Sources

- **Slide 1**: School building from Unsplash with blue fallback
- **Slide 2**: Students in classroom from Unsplash with green fallback
- **Slide 3**: School sports from Unsplash with red fallback
- **Virtual Tour**: School campus from Unsplash with gray fallback

## Features Added

✅ **Reliable Image URLs**: Updated Unsplash URLs with proper parameters
✅ **Fallback Images**: Placeholder images with school branding if main images fail
✅ **Loading Animation**: Visual loading indicator while images load
✅ **Error Handling**: Automatic fallback when images fail to load
✅ **Responsive Design**: Images properly sized for all devices

## Image Fallback System

Each carousel image has an `onerror` attribute that automatically loads a placeholder if the main image fails:

```html
<img
  src="main-image-url"
  onerror="this.src='https://via.placeholder.com/2000x800/color/white?text=Fallback+Text';"
  class="carousel-image"
/>
```

## Using Local Images (Optional)

If you prefer to use local images instead of external URLs:

1. **Download Images**: Run the download script

   ```bash
   python download_carousel_images.py
   ```

2. **Update Template**: Add static loading and update image sources

   ```django
   {% load static %}
   <img src="{% static 'core/images/school-building.jpg' %}" ...>
   ```

3. **Collect Static Files**:
   ```bash
   python manage.py collectstatic
   ```

## Troubleshooting

- **Images not loading**: Check internet connection and image URLs
- **Slow loading**: Images will show loading animation until loaded
- **Images broken**: Fallback placeholders will automatically display
- **Local images not found**: Ensure static files are collected properly

## Customization

To use your own school images:

1. Add images to `core/static/core/images/`
2. Update the template with new image paths
3. Ensure images are optimized (recommended: 2000x800px, <500KB each)
4. Run `python manage.py collectstatic`

## Status

✅ **FIXED** - Carousel images now load reliably with proper fallbacks
