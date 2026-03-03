import os
import sys

from celery_stuff.celery_app import celery

def main():
    env=os.environ.get("ENV","prod").lower()
    if env not in {"dev","test"}:
        print("manual_refresh is disabled outside dev/test",file=sys.stderr)
        return 2
    res=celery.send_task("celery_stuff.celery_app.refresh_db")
    print(res.id)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
