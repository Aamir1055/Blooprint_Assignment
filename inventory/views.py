from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from .models import InventoryItem
from .serializers import InventoryItemSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User registered: {serializer.data['username']}")
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        
        logger.error(f"User registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class CreateItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if an item with the same name already exists
        item_name = request.data.get('name')
        if InventoryItem.objects.filter(name=item_name).exists():
            logger.warning(f"Item creation failed: Item with name '{item_name}' already exists.")
            return Response({"error": "Item with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Cache the created item
            cache.set(f'inventory_{item.id}', serializer.data, timeout=60*15)
            logger.info(f"Item created: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Item creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id, *args, **kwargs):
        cached_item = cache.get(f'inventory_{item_id}')
        if cached_item:
            logger.info(f"Cache hit for item ID: {item_id}")
            return Response(cached_item, status=status.HTTP_200_OK)
        
        # If not found in cache, retrieve from the database
        item = get_object_or_404(InventoryItem, pk=item_id)
        serializer = InventoryItemSerializer(item)
        
        # Cache the retrieved item
        cache.set(f'inventory_{item_id}', serializer.data, timeout=60*15)
        logger.info(f"Item retrieved and cached: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(InventoryItem, pk=item_id)
        serializer = InventoryItemSerializer(item, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
          
            cache.set(f'inventory_{item_id}', serializer.data, timeout=60*15)
            logger.info(f"Item updated: {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.error(f"Item update failed for ID {item_id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(InventoryItem, pk=item_id)
        item_name = item.name
        item.delete()
        
        # Remove item from cache
        cache.delete(f'inventory_{item_id}')
        logger.info(f"Item deleted: {item_name}")
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)
