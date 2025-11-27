from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, UserRegistrationResponseSerializer
from rest_framework.permissions import AllowAny

class UserRegistrationView(generics.CreateAPIView):
    #  API endpoint for user registration.
    
    # a simple approach would be to use the default CreateAPIView
    # serializer_class = UserRegistrationSerializer
    

    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] 

    
    # using a more robust approach to control input and output
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Use response serializer to return clean data
        response_serializer = UserRegistrationResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)