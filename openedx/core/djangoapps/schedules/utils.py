

import datetime
import logging

import pytz
from django.db.models import F, Subquery
from django.db.models.functions import Greatest

from openedx.core.djangoapps.schedules.models import Schedule
from student.models import CourseEnrollment

LOG = logging.getLogger(__name__)


# TODO: consider using a LoggerAdapter instead of this mixin:
# https://docs.python.org/2/library/logging.html#logging.LoggerAdapter
class PrefixedDebugLoggerMixin(object):
    log_prefix = None

    def __init__(self, *args, **kwargs):
        super(PrefixedDebugLoggerMixin, self).__init__(*args, **kwargs)
        if self.log_prefix is None:
            self.log_prefix = self.__class__.__name__

    def log_debug(self, message, *args, **kwargs):
        """
        Wrapper around LOG.debug that prefixes the message.
        """
        LOG.debug(self.log_prefix + ': ' + message, *args, **kwargs)

    def log_info(self, message, *args, **kwargs):
        """
        Wrapper around LOG.info that prefixes the message.
        """
        LOG.info(self.log_prefix + ': ' + message, *args, **kwargs)


def reset_self_paced_schedule(user, course_key, use_availability_date=False):
    """
    Reset the user's schedule if self-paced.

    It does not create a new schedule, just resets an existing one.
    This is used, for example, when a user requests it or when an enrollment mode changes.

    Arguments:
        user (User)
        course_key (CourseKey or str)
        use_availability_date (bool): if False, reset to now, else reset to when user got access to course material
    """
    schedule = Schedule.objects.filter(
        enrollment__user=user,
        enrollment__course__id=course_key,
        enrollment__course__self_paced=True,
    )

    if use_availability_date:
        # Query enrollments to find availability date -- very similar to query above, but we can't reuse that query
        # object because mysql doesn't like a subquery of an update to reference the same table being updated.
        # Be careful attempting to remove this logic because you can't reproduce a problem locally -- in my own testing,
        # I could not reproduce in devstack, but it was happening on prod databases. So implementations vary.
        # See https://dev.mysql.com/doc/refman/8.0/en/subquery-restrictions.html
        enrollments = CourseEnrollment.objects.filter(
            user=user,
            course__id=course_key,
            course__self_paced=True,
        ).annotate(
            availability=Greatest(F('created'), F('course__start')),
        )
        schedule.update(start_date=Subquery(enrollments.values('availability')[:1]))
    else:
        schedule.update(start_date=datetime.datetime.now(pytz.utc))
