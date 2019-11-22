======
Design
======

Azafea runs as a main *controller* process, which launches multiple *processor*
processes. The processors are the ones pulling from Redis, and choosing the
appropriate *event handler* depending on which queue they got the event from.

Running multiple processors lets Azafea utilize the multiple cores in your CPU
better, to handle multiple events in parallel.

Azafea is designed to be agnostic of the types of events it processes.

This means it pulls from configured Redis queues, and passes the pulled values
to the appropriate *event handler*.

Each event handler has the knowledge about the events it is passed, their
incoming format, how to deserialize them, what to do with them and finally how
to store them in PostgreSQL.

That makes Azafea flexible so it can adapt to the needs of various
organizations: you can :doc:`write your own event handlers <queue-plugins>`
which will process your events just the way you want.

All of this is piloted by :doc:`the configuration file <configuration>`.
