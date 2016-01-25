from testrail_reporter.reporter import Reporter
try:
    from testrail_reporter._version import version as __version__
except ImportError:
    __version__ = "0.0.0"


__all__ = ['Reporter', '__version__']
