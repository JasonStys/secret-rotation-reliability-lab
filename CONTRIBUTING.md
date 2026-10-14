# Contributing and maintenance

Author: Jason Stys. Describe a reproducible synthetic case and its expected safety/behavior oracle. Do not include real credentials/private logs. Before a change, read the contracts/threat model and run the testing commands. Use semantic names, bounded inputs, explicit typed units, function/class contracts and comments for safety-critical reasoning.

Format first, then regenerate `scripts/code_map.py`; stage intended files and regenerate `scripts/file_guide.py`. Both checks gate CI. Keep folders shallow, add every tracked file to the README inventory, and update measured reports only from observed completed runs. Preserve independent negative/positive controls and final-main CI gates. Never weaken trust/ACL/expiry/advisory checks, use broad Docker deletion or add Actions artifacts/caches without discussing storage/privacy. Dependency/pin updates require actual audits and a fresh real drill.
