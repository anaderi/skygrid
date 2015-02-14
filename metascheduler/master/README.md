Minimal metascheduler
===


Installing
---

After installing everything to your `ship-env`, and working under it add some config-variables to `$VIRTUAL_ENV/bin/postactivate`:

```
#!/bin/bash
# This hook is sourced after this virtualenv is activated.
export SHIP_FRONTEND_CONFIG=<path-to-repo>/frontend.cfg
```


API
---

Basic API usage is in `../tests/queue.py` (relatevly to this file dir).

There is no heartbears in minimal implementation, API is the next:


* GET `/queue/<str:queue_name>` — get job from queue
* POST `/queue/<str:queue_name>` — add job to queue
* GET `/queue/<str:queue_name>/info` - returns info about queue: it existence and length

Jobs are described as dict in arbitrary format.
