import os
import sys

from celery_stuff.celery_app import refresh_db

def main():
    env=os.environ.get("ENV","prod").lower()
    if env not in {"dev","test"}:
        print("manual_refresh is disabled outside dev/test",file=sys.stderr)
        return 2
    res=refresh_db.delay()
    print(res.id)
    return 0

if __name__ == "__main__":
    sys.exit(main())
