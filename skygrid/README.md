Skygrid
===


Installing
---

After installing everything to your skygrid virtualenv, add next config-variables to `$VIRTUAL_ENV/bin/postactivate`:

```
#!/bin/bash
# This hook is sourced after this virtualenv is activated.
export SKYGRID_FRONTEND_CONFIG=<path-to-repo>/frontend.cfg
```


API
---
