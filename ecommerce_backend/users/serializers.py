# users/serializers.py
# defining user serializers to allow log in and sign up for this api 
from rest_framework import serializers
from django.contrib.auth import get_user_model

# custom user model defined in settings.py (users.CustomUser)
# with this, am referencing the CustomUser model, and I can do that from any file in the project
User = get_user_model() 

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration (creation of a new CustomUser).
    """
    # The password field is write-only for security (cannot be read back from API)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        # Fields the user must provide to register
        fields = ('id', 'email', 'first_name', 'last_name', 'password') 
        # the id is auto generated, and it is read-only
        read_only_fields = ('id',) 
    
    # Custom Create Method 
    # This method is crucial: it overrides the default behavior 
    # to ensure the password is set securely using set_password(), not saved as plain text.
    def create(self, validated_data):
        # 1. Extract the password before creating the user object
        password = validated_data.pop('password', None)
        
        # 2. Create the user object using the remaining validated data
        instance = self.Meta.model(**validated_data)
        
        # 3. Use the Django set_password method for secure hashing
        if password is not None:
            instance.set_password(password)
            
        # 4. Save the new user to the database
        instance.save()
        return instance