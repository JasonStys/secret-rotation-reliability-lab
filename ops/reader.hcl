# Jason Stys: application token can issue ONLY reader credentials; everything else remains default-deny.
# Path: database/creds/reader. Capability: read. No wildcard, root, configuration or revoke capabilities.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# symbol: capabilities — line 7
# END CODE MAP
path "database/creds/reader" {
  capabilities = ["read"]
}
