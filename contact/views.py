from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from .forms import ContactForm, MailingListForm
from .models import ContactMessage, MailingListSubscriber


def contact(request):
    form = ContactForm()
    mailing_form = MailingListForm()
    return render(request, 'contact/contact.html', {
        'form': form,
        'mailing_form': mailing_form,
    })


def contact_submit(request):
    """HTMX endpoint — returns a partial HTML snippet."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ContactForm(request.POST)
    if form.is_valid():
        msg = ContactMessage.objects.create(**form.cleaned_data)
        _send_contact_email(msg)
        return render(request, 'partials/contact_success.html')

    return render(request, 'partials/contact_form.html', {'form': form})


def mailing_list_subscribe(request):
    """HTMX endpoint for mailing list signup."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = MailingListForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        name = form.cleaned_data.get('name', '')
        MailingListSubscriber.objects.get_or_create(
            email=email,
            defaults={'name': name},
        )
        return render(request, 'partials/mailing_list_success.html')

    return render(request, 'partials/mailing_list_form.html', {'mailing_form': form})


def _send_contact_email(msg: ContactMessage):
    subject = f'[joshsite] {msg.subject}'
    body = (
        f'Name: {msg.name}\n'
        f'Email: {msg.email}\n\n'
        f'{msg.message}'
    )
    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER or 'noreply@joshuashneider.com',
        [settings.CONTACT_EMAIL],
        fail_silently=False,
    )
