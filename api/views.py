from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import base64
from .models import Book
from .serializers import BookSerializer
from .services.claude_service import simplify_text, suggest_title
from anthropic import Anthropic
from django.conf import settings
import logging
import os
logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_all_books(request):
    """Get all books"""
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
def process_text(request):
    logger.info(f"Request received: {request.data}")
    try:
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'No text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new book
        book = Book.objects.create(original_text=text)
        
        # Log before Claude API call
        logger.info("Calling Claude API for text simplification")
        
        # Simplify text using Claude
        simplified_text = simplify_text(text)
        
        # Log after Claude API call
        logger.info("Claude API call successful")
        
        # Process and create pages
        book.process_text(simplified_text)

        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in process_text: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_book(request, book_id):
    """Get a specific book and its pages"""
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response(serializer.data)

@api_view(['PATCH'])
def update_book(request, book_id):
    """Update book details"""
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_page(request, book_id):
    """Add a new page to an existing book"""
    book = get_object_or_404(Book, id=book_id)
    text = request.data.get('text', '')
    
    if not text:
        return Response(
            {'error': 'No text provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        # Simplify new text
        simplified_text = simplify_text(text)
        
        # Add as new page
        book.add_page(simplified_text)
        
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    """Handle image upload and text extraction using Claude"""
    try:
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_file = request.FILES['image']
        
        # Read the image file and encode it to base64
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Extract and simplify text using Claude
        from .services.claude_service import extract_text_from_image
        extracted_text = extract_text_from_image(image_data)
        
        return Response({
            'extracted_text': extracted_text
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_endpoint(request):
    """Test endpoint to verify API functionality"""
    return Response({
        "message": "API is working!",
        "environment": "production" if os.getenv('VERCEL') else "development"
    }, status=status.HTTP_200_OK)