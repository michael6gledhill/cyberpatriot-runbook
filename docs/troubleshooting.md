# Troubleshooting

## Login issues
- Verify email/password; use Copy button on errors.
- Admin/Coach auto-approve; others may be pending approval.

## Team creation
- Ensure Team ID format NN-NNNN.
- Creator is set automatically (admin/coach); if missing, update to latest code.

## Join requests
- Duplicate requests are blocked; check pending requests table.

## Detached session errors
- Fixed by eager-loading relationships in repositories. Update to latest code if seen.

## Database
- Confirm MySQL running and credentials in `config.py`.
- Re-run `init_database.py` if schema mismatch.
