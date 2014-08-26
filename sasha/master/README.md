SHIP-master
===


Installing
---

After installing everything to your `ship-env`, and working under it add some config-variables to `$VIRTUAL_ENV/bin/postactivate`:

```
#!/bin/bash
# This hook is sourced after this virtualenv is activated.
export SHIP_FRONTEND_CONFIG=<path-to-repo>/frontend.cfg
```


Как всё работает?
---

Эту часть хотелось бы для начала написать на русском.

Цепочка обсчёта задачи(job) для пользователя выглядит следующим образом:

1. Пользователь(User) отправляет задачу в мастер(MetaScheduler), делая POST-запрос на ручку `/add_job`. Описание формата задачи: [https://github.com/anaderi/skygrid/wiki/Job-descriptor](https://github.com/anaderi/skygrid/wiki/Job-descriptor)
2. Пользователю возвращается ID задачи, её состояние можно смотреть по ручке `/jobs/<job-id>`


Со стороны исполнителя(Worker) — вне зависимости YARN это или нет, последовательность выглядит следующим образом

1. При старте worker порождает heartbeat-процесс, который дёргает ручку `/beat/<worker-id>` с некотороым интервалом.
2. Когда worker решает, что ему нужны задачи, он обращается по ручке `/get_jobs`, которая возвращает ему `njob` задач(`njob` — параметр), задачи на стороне мастера помечаются как отданные worker'у.
3. После получения задач, воркер обязан сделать POST-запросы на `/jobs/<job-id>` с обновлением статусов задач(`submitted` -> `running`). Задачи с заданным worker'ом в статусе `submitted` инвалидируются через заданное время.
4. По завершении воркер сообщает об этом через api.



Основные компоненты master
---

1. __Ручка `/add_job`__: добавление задач от пользователя
2. __Ручка `/get_jobs`__: раздача задач worker'ам
3. __REST API `/jobs/<job-id>`__: GET запросы на получения статуса задач, POST на изменения состояния(от воркеров)
4. __Worker Watch__: воркеры помечаются как неактивные по timeout их hearbeat'а. Все задачи неактивного воркера инвалидируются.
5. __Job Watch__: Задачи с заданным worker'ом в статусе `submitted` инвалидируются по таймауту.

