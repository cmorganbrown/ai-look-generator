# AI-Generated Shoppable Looks Feature

## Overview

The AI Look Generation feature allows users to create stunning, AI-generated lifestyle scenes from selected products on landing pages. This feature uses OpenAI's DALL-E 3 image generation to create high-fidelity, shoppable looks that combine multiple products into cohesive interior design scenes.

## How It Works

### 1. Product Selection
- Browse any landing page (e.g., "Moody Dark Powder Room")
- Hover over products to reveal selection checkboxes
- Select 3 or more products you want to combine in a look
- A floating control panel appears showing your selection count

### 2. AI Look Generation
- Click "Generate AI Look" when you have 3+ products selected
- The system analyzes your selected products and creates a detailed prompt
- OpenAI's DALL-E 3 generates a high-quality lifestyle image
- The generated image is saved and a new look page is created

### 3. Look Pages
Each generated look features:
- **Hero Image**: The AI-generated lifestyle scene
- **Featured Products**: Carousel of the exact products used in the look
- **All Products**: Grid of all products from the original landing page
- **Shopping Links**: Direct links to purchase each product

## Features

### High Fidelity Generation
- Analyzes product titles, descriptions, and visual elements
- Extracts colors, materials, and styles automatically
- Determines room type (bedroom, bathroom, living room, etc.)
- Creates professional interior design prompts

### Smart Product Analysis
- **Visual Elements**: Extracts colors, materials, and styles
- **Room Detection**: Identifies room type from product context
- **Style Matching**: Determines design aesthetic (modern, traditional, rustic, etc.)
- **Cohesive Styling**: Ensures products work together visually

### User Experience
- **Selection Interface**: Intuitive checkbox selection with visual feedback
- **Real-time Counter**: Shows selection progress (minimum 3 products)
- **Loading States**: Clear feedback during generation
- **Error Handling**: Graceful error messages and recovery

## Technical Implementation

### Backend Components

#### LookGenerator Class (`look_generator.py`)
- Handles OpenAI API integration
- Manages image generation and storage
- Processes product data for prompt creation
- Stores look metadata and relationships

#### Flask Routes
- `/looks` - Gallery of all generated looks
- `/looks/<look_id>` - Individual look page
- `/generate_look` - API endpoint for look generation
- `/looks/images/<filename>` - Serves generated images

### Frontend Components

#### Product Selection
- Checkbox overlays on product cards
- Visual selection feedback (borders, shadows)
- Floating control panel with counter
- Clear selection functionality

#### Look Pages
- Hero image display
- Product carousel for featured items
- Grid layout for all products
- Responsive design for all devices

## Setup Requirements

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Directory Structure
```
TrendScraper/
├── looks/
│   ├── data/          # Look metadata JSON files
│   └── images/        # Generated look images
├── landing_pages/     # Original landing pages
├── uploads/          # Scraped data files
└── templates/        # Flask templates
```

## Usage Examples

### Creating a Bathroom Look
1. Navigate to "Moody Dark Powder Room" landing page
2. Select: Vanity, Mirror, Towel Rack, Bath Rug
3. Click "Generate AI Look"
4. View the generated bathroom scene
5. Shop the featured products

### Creating a Bedroom Look
1. Navigate to "Nancy Meyers Bedroom" landing page
2. Select: Bed Frame, Nightstand, Lamp, Throw Pillows
3. Click "Generate AI Look"
4. View the generated bedroom scene
5. Shop the featured products

## API Integration

### Generate Look Endpoint
```javascript
POST /generate_look
{
  "products": [
    {
      "title": "Product Name",
      "price": "$299",
      "image": "image_url",
      "url": "product_url",
      "source": "Pinterest"
    }
  ],
  "landing_page_name": "moody-dark-powder-room.html"
}
```

### Response
```javascript
{
  "success": true,
  "look_id": "uuid-here",
  "look_url": "/looks/uuid-here",
  "message": "Look generated successfully!"
}
```

## Cost Considerations

- **OpenAI API**: DALL-E 3 costs approximately $0.04 per image
- **Storage**: Generated images are stored locally
- **Bandwidth**: Images served from local storage

## Future Enhancements

### Planned Features
- **Style Customization**: User-defined style preferences
- **Look Variations**: Multiple style options per product set
- **Social Sharing**: Share looks on social media
- **Look Collections**: Organize looks into themed collections
- **Product Recommendations**: Suggest additional products for looks

### Technical Improvements
- **Caching**: Cache generated images to reduce API calls
- **Batch Processing**: Generate multiple looks simultaneously
- **Quality Optimization**: Fine-tune prompts for better results
- **Mobile Optimization**: Enhanced mobile selection interface

## Troubleshooting

### Common Issues

**"OpenAI API key not configured"**
- Set the OPENAI_API_KEY environment variable
- Restart the Flask application

**"No products found"**
- Ensure landing page has products loaded
- Check that product data is properly formatted

**"Error generating look"**
- Verify OpenAI API key is valid
- Check internet connection
- Ensure sufficient API credits

**"Image not displaying"**
- Check that looks/images/ directory exists
- Verify file permissions
- Check image file integrity

## Support

For issues or questions about the AI Look Generation feature:
1. Check the troubleshooting section above
2. Review the Flask application logs
3. Verify OpenAI API status and credits
4. Test with a simple product selection first 