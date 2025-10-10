# Roll20 Service

Our Roll20 Service is used by this application to interact with Roll20. Because Roll20 has no public API, this service
uses a browser to connect using the Roll20 website.

## Service States

- Connecting
- Ready
- Sending
- Closed

## Service Methods

- `open()` - connects and gets set up. State will be `Ready` when this completes successfully.
- `send(to_users, message)` - sends a whisper message to each of the given users in the Roll20 chat. Service transitions
  to `Sending` state while sending, then returns to `Ready`.
- `close()` - closes the connection.

### Details
- Calling send() while the service is already sending will queue the message to be sent after the current message is
  sent.
