# TLS certificate expired or expiring

Owner: security-engineering.

## Symptoms

- Clients fail with handshake errors: "x509: certificate has expired or is not yet valid".
- Sudden spike in 5xx or connection resets on an ingress or gateway, with no deploy.
- Synthetic canaries fail on HTTPS checks.

## Likely causes

- Automatic renewal failed (DNS validation broken, expired credentials for the issuer).
- A certificate was manually uploaded and never added to automated renewal.
- An intermediate certificate in the chain expired.

## Diagnosis

1. Check the certificate's notAfter date on the failing endpoint.
2. Review renewal job logs for the certificate manager.
3. Confirm whether the full chain, including intermediates, is being served.

## Mitigation

1. Renew or re-issue the certificate and redeploy it to the gateway.
2. If renewal is blocked, fail traffic over to a region whose certificate is still valid.
3. Add the certificate to automated renewal and an expiry alarm at 30, 14, and 7 days.

## Escalation

Page security-engineering immediately for customer-facing endpoints.
