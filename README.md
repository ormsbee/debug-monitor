# Debug Monitor

Experimental debug monitoring tool (server + terminal UI) that is absolutely not
ready for real use or contributions yet. My first use case is for debugging
Django projects.

## Primary Goals

The Django Debug Toolbar has long been the go-to standard for debugging things
in the Django world. It's an outstanding project and every Django developer
should install it by default when developing their projects. I'm making this
because I had a few goals that I don't think fit well with its design. I would
like Debug Monitor to:

1. Run seamlessly in the scenario where there are many REST API requests being
made as part of loading a page.
2. Better support asynchronous use cases (channels, async views, celery, etc.)
by live-updating data as it comes in.
3. Eventually support multiple server instances reporting simultaneously (i.e.
when you're running multiple services).
4. Eventually support multiple server stacks in addition to Django.
5. Make it very easy to report new kinds of information without updating plugins
for debug-monitor itself.

That last one might be a bit puzzling. Imagine the situation where you are
working with something like Open edX (my day job), which is comprised of a
number of different services worked on by many different groups of people. If
one of those teams decides to add a plugin that sends a little extra bit of
information to the debug-monitor (e.g. a student's enrollment details), that
should not require anything to be installed in the debug-monitor itself.

This means that debug-monitor is going to have some first class concepts that it
really understands (like request/response, and chained requests), and a bunch of
other data that it just knows how to dumbly display. Plugins that send messages
to it must create those messages using primitives that debug-monitor will
undersatnd, like ("append this to panel X", "this is a table", "this is Markdown
to render", etc.). Most of this data will be associated with request-specific
UUIDs, which is the responsibility of the senders to generate.

## Personal Goals

There are a lot of technologies here that I've wanted to play around with for a
while but are still fairly new to me: asyncio, ZeroMQ, Textual/Rich, and Django
internals (especially around async).

## Non-Goals

I do *not* want Debug Monitor to be used on production sites. There are a host
of security and performance considerations that will complicate things in those
use cases, and it's not my goal to try to address them. There are big companies
with very robust APM solutions here.
