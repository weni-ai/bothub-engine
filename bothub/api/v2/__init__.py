from rest_framework import permissions


READ_METHODS = permissions.SAFE_METHODS
WRITE_METHODS = ['POST']
EDIT_METHODS = ['PUT', 'PATCH']
DELETE_METHODS = ['DELETE']
ADMIN_METHODS = ['DELETE']
