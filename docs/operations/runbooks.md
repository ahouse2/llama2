# Operations Runbooks

## Daily Checklist
- [ ] Validate ingestion Prefect flow succeeded overnight.
- [ ] Review retriever quality dashboard for anomaly alerts.
- [ ] Confirm GitHub Actions CI pipeline completed successfully.

## Incident Response
1. Page the on-call engineer through PagerDuty with the "Discovery Platform" service.
2. Capture the failing payloads and Prefect task IDs.
3. Roll back to the latest green deployment using Helm within the `infra` workspace.

## Maintenance Windows
- Scheduled Sundays 02:00–04:00 UTC.
- Use Terraform workspaces for environment promotion and Helm for zero-downtime rollouts.
