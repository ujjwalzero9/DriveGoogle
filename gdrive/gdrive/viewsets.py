import hashlib
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import User, Entity
from .serializers import UserSerializer, EntitySerializer, LoginSerializer
from .decorators import auth_layer
import boto3

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email)
                # Check if the provided password is correct
                if user.password == password:
                    return Response({'message': 'Login successful', 'token': user.token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @auth_layer
    def get_presigned_url(self, request, *args, **kwargs):
        filename = request.data.get('filename')
        if not filename:
            return Response({'error': 'Filename is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a pre-signed URL for the S3 bucket
        s3_client = boto3.client(
            's3',
            aws_access_key_id='AKIAWBUEWYQO5KGVHBVY',
            aws_secret_access_key='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'
        )
        post = s3_client.generate_presigned_post(
            Bucket='backendc',
            Key=filename,
            ExpiresIn=3600
        )

        return Response({'post': post}, status=status.HTTP_200_OK)

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    def get_folder_contents(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        folder_path = "/"

        try:
            hashpath = self.generate_hashpath(folder_path, user_id)

            entities = Entity.objects.filter(hashpath=hashpath)

            if not entities.exists():
                return Response({"error": "No entities found for the specified user ID"},
                                status=status.HTTP_404_NOT_FOUND)

            serialized_entities = EntitySerializer(entities, many=True).data
            return Response(serialized_entities, status=status.HTTP_200_OK)

        except Entity.DoesNotExist:
            return Response({"error": "Entities not found for the specified user ID"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @auth_layer
    def delete_folder(self, request):
        folder_id = request.data.get('id')
        if not folder_id:
            return Response({"error": "Folder ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = self.get_queryset().get(pk=folder_id)
            self.perform_destroy(instance)
            return Response({"status": "Folder Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Entity.DoesNotExist:
            return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def generate_hashpath(folder_path, user_id):
        data = f"{folder_path}{user_id}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        return hash_value

    @auth_layer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    @auth_layer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
