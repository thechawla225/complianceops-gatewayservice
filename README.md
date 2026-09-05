API Gateway service:
This Service is the first service in the flow, it will authenticate the user, and send the transaction to the Transaction service for actual processing.

This service accepets transactions in MT103 and Pacs.008 format, processes it into a standard format and then sends it upstream.
