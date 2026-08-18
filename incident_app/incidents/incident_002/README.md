Incident 002 — Order Notification Service Failure

The Orders API is successfully creating orders, but the notification step is failing and causing the request to return HTTP 500.

The incident started after a recent application configuration change. The notification service is expected to be called after an order is created.

Observed behavior:

Orders can be created successfully.
The notification request fails.
The API returns HTTP 500.
The application log reports a failure when attempting to contact the notification service.

The investigation should determine why the notification service call is failing and identify the appropriate remediation.