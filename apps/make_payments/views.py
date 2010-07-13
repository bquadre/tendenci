from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from make_payments.forms import MakePaymentForm
from make_payments.utils import make_payment_inv_add, make_payment_email_user
from make_payments.models import MakePayment
from site_settings.utils import get_setting
from base.http import Http403
from base.utils import tcurrency
from event_logs.models import EventLog
from perms.utils import get_notice_recipients

try:
    from notification import models as notification
except:
    notification = None


def add(request, form_class=MakePaymentForm, template_name="make_payments/add.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        
        if form.is_valid():
            mp = form.save(commit=False)
            # we might need to create a user record if not exist
            if request.user.is_authenticated():
                user = request.user
            else:
                try:
                    user = User.objects.get(email=mp.email)
                except:
                    user = request.user

            if not user.is_anonymous():
                mp.user = user
                mp.creator = user
                mp.creator_username = user.username
            mp.save(user)
            
            # create invoice
            invoice = make_payment_inv_add(user, mp)
            # log an event for invoice add
            log_defaults = {
                'event_id' : 311000,
                'event_data': '%s (%d) added by %s' % (invoice._meta.object_name, invoice.pk, request.user),
                'description': '%s added' % invoice._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': invoice,
            }
            EventLog.objects.log(**log_defaults)  
            
            # updated the invoice_id for mp, so save again
            mp.save(user)
            
            # log an event for make_payment
            log_defaults = {
                'event_id' : 671000,
                'event_data': '%s (%d) added by %s' % (mp._meta.object_name, mp.pk, request.user),
                'description': '%s added' % mp._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': mp,
            }
            EventLog.objects.log(**log_defaults)
            
            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'payments', 'paymentrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'mp': mp,
                        'invoice': invoice,
                        'request': request,
                    }
                    notification.send_emails(recipients,'make_payment_added', extra_context)
            
            # email to user 
            email_receipt = form.cleaned_data['email_receipt']
            if email_receipt:
                make_payment_email_user(request, mp, invoice)
            
            # redirect to online payment or confirmation page
            if mp.payment_method == 'cc' or mp.payment_method == 'credit card':
                return HttpResponseRedirect(reverse('payments.views.pay_online', args=[invoice.id, invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('make_payment.add_confirm', args=[mp.id]))
    else:
        form = form_class(request.user)

    currency_symbol = get_setting("site", "global", "currencysymbol")
    if not currency_symbol: currency_symbol = "$"
       
    return render_to_response(template_name, {'form':form, 'currency_symbol': currency_symbol}, 
        context_instance=RequestContext(request))
    
def add_confirm(request, id, template_name="make_payments/add_confirm.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))

def view(request, id=None, template_name="make_payments/view.html"):
    mp = get_object_or_404(MakePayment, pk=id)
    if not mp.allow_view_by(request.user): raise Http403
    
    mp.payment_amount = tcurrency(mp.payment_amount)
    return render_to_response(template_name, {'mp':mp}, 
        context_instance=RequestContext(request))
    
    
    