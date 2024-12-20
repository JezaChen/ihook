# Custom Package Sample

This is the sample code of custom package, for unit testing.

- When importing `pkg_a`, it will import `mod_b` and `pkg_d` as well.
- When importing `pkg_a.pkg_d`, it will import `pkg_a.pkg_d.mod_e` as well.
- When importing `pkg_a.pkg_g`, it will import `pkg_a.pkg_g.mod_h` as well.
- When each module is imported, a message will be printed to the console.
