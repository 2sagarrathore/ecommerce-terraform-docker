# Captured evidence

Raw output taken from the live deployment on 17 October 2026 before teardown.

| File | Source |
| --- | --- |
| `vpc.txt`, `subnet.txt`, `instance.txt` | `aws ec2 describe-*` |
| `security-group-rules.txt`, `.json` | `aws ec2 describe-security-group-rules` |
| `console-output-raw.txt` | `aws ec2 get-console-output --latest` |
| `user-data-deployment.log` | the above, with kernel timestamps stripped |

**Redaction:** the admin CIDR that `allowed_http_cidr` was narrowed to is a home
IP address, so it appears here as `203.0.113.4/32` (a RFC 5737 documentation
address) instead of the real value. Nothing else has been altered.
