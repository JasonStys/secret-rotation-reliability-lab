-- Jason Stys: fictional product inventory and dedicated non-superuser credential manager privileges.
-- Variables: none. Fixed table inventory(id, product, quantity); no user-controlled SQL identifiers.
-- BEGIN CODE MAP (generated; python scripts/code_map.py)
-- column: id — line 11
-- column: product — line 11
-- column: quantity — line 11
-- table: inventory — line 11
-- END CODE MAP
REVOKE ALL ON DATABASE lab FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE TABLE inventory (id INTEGER PRIMARY KEY, product TEXT NOT NULL, quantity INTEGER NOT NULL CHECK (quantity >= 0));
INSERT INTO inventory VALUES (1, 'Fictional sensor module', 12), (2, 'Fictional gateway', 7);
GRANT CONNECT ON DATABASE lab TO bao_manager WITH GRANT OPTION;
GRANT USAGE ON SCHEMA public TO bao_manager WITH GRANT OPTION;
GRANT SELECT ON inventory TO bao_manager WITH GRANT OPTION;
