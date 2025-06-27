import openai
import os
import json
import uuid
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO

class LookGenerator:
    def __init__(self, openai_api_key=None):
        """Initialize the Look Generator with OpenAI API key"""
        self.openai_client = None
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        elif os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Create directories for storing looks
        self.looks_dir = 'looks'
        self.looks_data_dir = os.path.join(self.looks_dir, 'data')
        self.looks_images_dir = os.path.join(self.looks_dir, 'images')
        
        for directory in [self.looks_dir, self.looks_data_dir, self.looks_images_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def generate_shoppable_look(self, selected_products, style_prompt=None, landing_page_name=None):
        """Generate a shoppable look from selected products"""
        
        if not self.openai_client:
            raise Exception("OpenAI API key not configured")
        
        if len(selected_products) < 3:
            raise Exception("Need at least 3 products to create a look")
        
        # Build detailed product description for high fidelity
        product_desc = self._build_product_description(selected_products)
        
        # Create style prompt if not provided
        if not style_prompt:
            style_prompt = self._generate_style_prompt(selected_products)
        
        # Build the full prompt for ChatGPT image generation
        full_prompt = self._build_image_prompt(product_desc, style_prompt)
        
        try:
            # Generate image using ChatGPT's image generation service
            response = self.openai_client.images.generate(
                model="dall-e-3",  # Using DALL-E 3 for high fidelity
                prompt=full_prompt,
                n=1,
                size="1024x1024",
                quality="hd",
                style="natural"
            )
            
            image_url = response.data[0].url
            
            # Download and save the image
            look_id = str(uuid.uuid4())
            image_filename = f"{look_id}.png"
            image_path = os.path.join(self.looks_images_dir, image_filename)
            
            self._download_and_save_image(image_url, image_path)
            
            # Create look data
            look_data = {
                'id': look_id,
                'landing_page': landing_page_name,
                'products': selected_products,
                'style_prompt': style_prompt,
                'image_filename': image_filename,
                'created_at': datetime.now().isoformat(),
                'product_count': len(selected_products)
            }
            
            # Save look data
            data_filename = f"{look_id}.json"
            data_path = os.path.join(self.looks_data_dir, data_filename)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(look_data, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'look_id': look_id,
                'image_path': image_path,
                'image_url': f'/looks/images/{image_filename}',
                'data': look_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_product_description(self, products):
        """Build a detailed description of selected products for high fidelity"""
        descriptions = []
        
        for product in products:
            title = product.get('title', 'Unknown product')
            price = product.get('price', 'Price not available')
            description = product.get('description', '')
            
            # Extract key visual elements from title/description
            visual_elements = self._extract_visual_elements(title, description)
            
            product_desc = f"{title} (${price})"
            if visual_elements:
                product_desc += f" - {visual_elements}"
            
            descriptions.append(product_desc)
        
        return "Create a cohesive lifestyle image featuring: " + "; ".join(descriptions)
    
    def _extract_visual_elements(self, title, description):
        """Extract visual elements from product title and description"""
        text = f"{title} {description}".lower()
        
        # Common visual elements to look for
        elements = []
        
        # Colors
        colors = ['white', 'black', 'gray', 'brown', 'beige', 'cream', 'navy', 'blue', 'green', 'red', 'pink', 'purple', 'gold', 'silver', 'brass', 'bronze']
        for color in colors:
            if color in text:
                elements.append(color)
        
        # Materials
        materials = ['wood', 'metal', 'glass', 'ceramic', 'fabric', 'leather', 'velvet', 'linen', 'cotton', 'silk', 'marble', 'granite', 'concrete']
        for material in materials:
            if material in text:
                elements.append(material)
        
        # Styles
        styles = ['modern', 'traditional', 'rustic', 'industrial', 'minimalist', 'bohemian', 'scandinavian', 'mid-century', 'contemporary', 'vintage']
        for style in styles:
            if style in text:
                elements.append(style)
        
        return ", ".join(elements[:3]) if elements else ""
    
    def _generate_style_prompt(self, products):
        """Generate a style prompt based on the selected products"""
        # Analyze products to determine room type and style
        titles = [p.get('title', '').lower() for p in products]
        
        # Determine room type
        room_type = "interior space"
        if any(word in " ".join(titles) for word in ['bed', 'nightstand', 'dresser']):
            room_type = "bedroom"
        elif any(word in " ".join(titles) for word in ['sofa', 'coffee', 'tv', 'entertainment']):
            room_type = "living room"
        elif any(word in " ".join(titles) for word in ['vanity', 'bath', 'toilet', 'shower']):
            room_type = "bathroom"
        elif any(word in " ".join(titles) for word in ['table', 'chair', 'dining']):
            room_type = "dining room"
        elif any(word in " ".join(titles) for word in ['desk', 'office', 'study']):
            room_type = "home office"
        
        # Determine style
        style = "modern cohesive design"
        if any(word in " ".join(titles) for word in ['traditional', 'classic', 'antique']):
            style = "traditional elegant design"
        elif any(word in " ".join(titles) for word in ['rustic', 'farmhouse', 'country']):
            style = "rustic warm design"
        elif any(word in " ".join(titles) for word in ['industrial', 'metal', 'concrete']):
            style = "industrial modern design"
        elif any(word in " ".join(titles) for word in ['minimalist', 'simple', 'clean']):
            style = "minimalist clean design"
        
        return f"{room_type} with {style}, professional photography, high-end interior design magazine style"
    
    def _build_image_prompt(self, product_desc, style_prompt):
        """Build the complete image generation prompt"""
        return f"""
{product_desc}. 

Style: {style_prompt}

Requirements:
- High fidelity to the actual products
- Professional interior design photography
- Cohesive color scheme and styling
- Natural lighting
- Magazine-quality composition
- Products should be clearly visible and recognizable
- Create a realistic, shoppable lifestyle scene
"""
    
    def _download_and_save_image(self, image_url, save_path):
        """Download and save the generated image"""
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
    
    def get_all_looks(self):
        """Get all generated looks"""
        looks = []
        
        if not os.path.exists(self.looks_data_dir):
            return looks
        
        for filename in os.listdir(self.looks_data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.looks_data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        look_data = json.load(f)
                        look_data['image_url'] = f'/looks/images/{look_data["image_filename"]}'
                        looks.append(look_data)
                except Exception as e:
                    print(f"Error loading look {filename}: {e}")
        
        # Sort by creation date (newest first)
        looks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return looks
    
    def get_look_by_id(self, look_id):
        """Get a specific look by ID"""
        data_path = os.path.join(self.looks_data_dir, f"{look_id}.json")
        
        if not os.path.exists(data_path):
            return None
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                look_data = json.load(f)
                look_data['image_url'] = f'/looks/images/{look_data["image_filename"]}'
                return look_data
        except Exception as e:
            print(f"Error loading look {look_id}: {e}")
            return None 