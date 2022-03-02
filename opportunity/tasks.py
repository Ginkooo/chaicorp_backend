from celery import Celery
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from common.models import Profile
from opportunity.models import Opportunity

app = Celery("redis://")


@app.task
def send_email_to_assigned_user(
    recipients, opportunity_id
):
    """ Send Mail To Users When they are assigned to a opportunity """
    opportunity = Opportunity.objects.get(id=opportunity_id)
    created_by = opportunity.created_by
    for user in recipients:
        if profile := Profile.objects.filter(id=user, is_active=True).first():
            recipients_list = [profile.user.email]
            context = {
                "url": settings.DOMAIN_NAME,
                "user": profile.user,
                "opportunity": opportunity,
                "created_by": created_by,
            }

            subject = "Assigned an opportunity for you."
            html_content = render_to_string(
                "assigned_to/opportunity_assigned.html", context=context
            )

            msg = EmailMessage(subject, html_content, to=recipients_list)
            msg.content_subtype = "html"
            msg.send()
