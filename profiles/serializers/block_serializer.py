from rest_framework import serializers
from ..models.block import Block

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['blocker', 'blocked']
        read_only_fields = ['blocker']
