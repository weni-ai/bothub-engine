from django.dispatch import Signal
from django.db import reset_queries, close_old_connections


message_started = Signal()
message_finished = Signal()

# db connection state managed similarly to the wsgi handler
message_started.connect(reset_queries)
message_started.connect(close_old_connections)
message_finished.connect(close_old_connections)
