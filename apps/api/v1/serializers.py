"""
API v1 Serializers.
"""
from rest_framework import serializers
from apps.queues.models import QueueToken
from apps.branches.models import Branch, Department, Service

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'code']

class DepartmentSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    class Meta:
        model = Department
        fields = ['id', 'name', 'branch']

class ServiceSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'name', 'token_prefix', 'estimated_time_mins', 'department']

class QueueTokenSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = QueueToken
        fields = ['id', 'token_number', 'user', 'service', 'status', 'created_at', 'updated_at']
        read_only_fields = ['token_number', 'status', 'created_at', 'updated_at']
