import logging, sys, structlog

def configure():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )

configure()
log = structlog.get_logger()
