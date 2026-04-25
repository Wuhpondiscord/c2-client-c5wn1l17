# C2 Client Simulation (Ethical Demo)

This Space runs a client that polls the C2 server at:
**`https://wuhp-notac2.hf.space`**

## Security Notice
- This is an educational demonstration only
- All network requests are limited to loopback addresses (127.x.x.x)
- No actual malicious activity is performed
- Tokens are managed by the C2 server, not embedded in this Space

## Configuration
The client polls `https://wuhp-notac2.hf.space/api/poll_command` for commands and reports results to `https://wuhp-notac2.hf.space/api/report`.
