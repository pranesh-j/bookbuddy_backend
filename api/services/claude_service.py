# api/services/claude_service.py
import anthropic
from django.conf import settings
import re

def extract_text_from_image(image_data):
    """Extract and simplify text from image using Claude"""
    try:
        client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        prompt = """Extract the text from this image without any formatting or prefixes."""
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        )

        # Get content and clean it
        content = str(message.content)
        
        # Remove TextBlock formatting if present
        if 'TextBlock' in content:
            match = re.search(r"text=['\"](.+?)['\"],\s*type=['\"]text['\"]", content, re.DOTALL)
            if match:
                content = match.group(1)
        
        # Clean up the text
        content = content.replace('\\n', ' ').replace('\n\n\n', '\n\n').strip()
        
        return content

    except Exception as e:
        print(f"Error with Claude API: {str(e)}")
        raise

def simplify_text(text):
    """Simplifies text using Claude API"""
    try:
        client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        prompt = """Simplify this text to make it easier to understand. replace the hard or the complicated words with simple easy to understand words, Use clear, simple language while keeping the important information without removing anything or adding extra things, just modify the sentences in easy to understand format and do not remove any sentence. Make it more readable but maintain the key points. Return just the simplified text without any prefixes or formatting:

        {text}"""
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt.format(text=text)}]
        )

        # Get content and clean it
        content = str(message.content)
        
        # Remove TextBlock formatting if present
        if 'TextBlock' in content:
            match = re.search(r"text=['\"](.+?)['\"],\s*type=['\"]text['\"]", content, re.DOTALL)
            if match:
                content = match.group(1)
        
        return content.strip()

    except Exception as e:
        print(f"Error with Claude API: {str(e)}")
        raise

def suggest_title(text):
    """Generate a title suggestion using Claude API"""
    try:
        client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        prompt = """Generate a short, descriptive title (2-4 words) for this text. The title should be concise but meaningful. Just return the title directly without any explanation or prefix:

        {text}"""
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt.format(text=text)}]
        )
        
        response_text = str(message.content)
        
        # Apply same TextBlock extraction for title if needed
        if 'TextBlock' in response_text:
            match = re.search(r"text='(.*?)', type='text'", response_text)
            if match:
                return match.group(1)
                
        return response_text or "Untitled Book"

    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return "Untitled Book"