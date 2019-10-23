from rest_framework import permissions


READ_METHODS = permissions.SAFE_METHODS
WRITE_METHODS = ["POST", "PUT", "PATCH"]
ADMIN_METHODS = ["DELETE"]
