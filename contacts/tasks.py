from celery import Celery
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from common.models import Profile
from contacts.models import Contact

app = Celery("redis://")


@app.task
def send_email_to_assigned_user(
    recipients, contact_id
):
    """ Send Mail To Users When they are assigned to a contact """
    contact = Contact.objects.get(id=contact_id)
    created_by = contact.created_by
    for profile_id in recipients:
        if profile := Profile.objects.filter(
            id=profile_id, is_active=True
        ).first():
            recipients_list = [profile.user.email]
            context = {
                "url": settings.DOMAIN_NAME,
                "user": profile.user,
                "contact": contact,
                "created_by": created_by,
            }

            subject = "Assigned a contact for you."
            html_content = render_to_string(
                "assigned_to/contact_assigned.html", context=context
            )

            msg = EmailMessage(subject, html_content, to=recipients_list)
            msg.content_subtype = "html"
            msg.send()
