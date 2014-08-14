SHIP-master readme
===

After installing everything to your `ship-env`, and working under it add some config-variables to `$VIRTUAL_ENV/bin/postactivate`:

```
#!/bin/bash
# This hook is sourced after this virtualenv is activated.
export SHIP_FRONTEND_CONFIG=<path-to-repo>/frontend.cfg
```

