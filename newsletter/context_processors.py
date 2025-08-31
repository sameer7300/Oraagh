from .forms import SubscriberForm

def newsletter_form(request):
    return {'newsletter_form': SubscriberForm()}
