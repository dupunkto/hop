from datetime import datetime, timezone


def ensure_tz(dt, local=True):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.astimezone() if local else dt.replace(tzinfo=timezone.utc)
    return dt.astimezone()


def timeago_filter(value, local=True):
    value = ensure_tz(value, local=local)
    if value is None:
        return "never"

    now = datetime.now(timezone.utc)
    secs = int((now - value).total_seconds())
    future = secs < 0
    secs = abs(secs)

    def fmt(n, singular, plural):
        return f"{n} {singular if n == 1 else plural}"

    if secs < 1:
        return "now"

    if secs < 60:
        unit = fmt(secs, "second", "seconds")
    elif secs < 3600:
        unit = fmt(secs // 60, "minute", "minutes")
    elif secs < 86400:
        unit = fmt(secs // 3600, "hour", "hours")
    elif secs < 604800:
        unit = fmt(secs // 86400, "day", "days")
    elif secs < 2629800:
        unit = fmt(secs // 604800, "week", "weeks")
    elif secs < 31557600:
        unit = fmt(secs // 2629800, "month", "months")
    else:
        unit = fmt(secs // 31557600, "year", "years")

    return f"in {unit}" if future else f"{unit} ago"


FILTERS = {
    "timeago": timeago_filter,
}


def register_filters(app):
    for name, fn in FILTERS.items():
        app.template_filter(name)(fn)
