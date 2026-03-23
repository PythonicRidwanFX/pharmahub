import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Plan, Subscription, Payment
from .utils import create_subscription
from .paystack import initialize_transaction, verify_transaction, PaystackError


@login_required
def plan_list(request):
    plans = Plan.objects.filter(is_active=True)
    current_subscription = Subscription.objects.filter(
        pharmacy=request.user.pharmacy,
        is_current=True
    ).first()

    return render(request, 'subscriptions/plan_list.html', {
        'plans': plans,
        'current_subscription': current_subscription,
    })


@login_required
def subscription_status(request):
    current_subscription = Subscription.objects.filter(
        pharmacy=request.user.pharmacy,
        is_current=True
    ).first()

    return render(request, 'subscriptions/subscription_status.html', {
        'current_subscription': current_subscription
    })


@login_required
def choose_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)

    # unique reference
    reference = f"PHARM_{uuid.uuid4().hex[:16].upper()}"

    payment = Payment.objects.create(
        pharmacy=request.user.pharmacy,
        plan=plan,
        amount=plan.price,
        reference=reference,
        email=request.user.email,
        status='pending',
        payment_gateway='paystack'
    )

    callback_url = request.build_absolute_uri(
        reverse('payment_callback')
    )

    metadata = {
        "pharmacy_id": request.user.pharmacy.id,
        "plan_id": plan.id,
        "payment_id": payment.id,
    }

    try:
        # Paystack amount is in kobo for NGN
        amount_kobo = int(Decimal(plan.price) * 100)

        data = initialize_transaction(
            email=request.user.email,
            amount_kobo=amount_kobo,
            reference=reference,
            callback_url=callback_url,
            metadata=metadata
        )

        payment.access_code = data.get('access_code')
        payment.save(update_fields=['access_code'])

        return redirect(data['authorization_url'])

    except PaystackError as e:
        payment.status = 'failed'
        payment.gateway_response = str(e)
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, f'Unable to start payment: {e}')
        return redirect('plan_list')


@login_required
def payment_callback(request):
    reference = request.GET.get('reference')

    if not reference:
        messages.error(request, 'Missing payment reference.')
        return redirect('plan_list')

    payment = get_object_or_404(
        Payment,
        reference=reference,
        pharmacy=request.user.pharmacy
    )

    if payment.status == 'success':
        messages.success(request, 'Payment already verified.')
        return redirect('subscription_status')

    try:
        verified = verify_transaction(reference)
        status = verified.get('status')
        paid_amount = verified.get('amount')  # in kobo
        expected_amount = int(payment.amount * 100)

        payment.gateway_response = verified.get('gateway_response', '')

        if status == 'success' and paid_amount == expected_amount:
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.save(update_fields=['status', 'paid_at', 'gateway_response'])

            create_subscription(
                pharmacy=request.user.pharmacy,
                plan=payment.plan,
                status='active'
            )

            messages.success(request, 'Payment verified successfully. Subscription activated.')
            return redirect('subscription_status')

        payment.status = 'failed'
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, 'Payment verification failed or amount mismatch.')
        return redirect('plan_list')

    except PaystackError as e:
        messages.error(request, f'Payment verification failed: {e}')
        return redirect('plan_list')


@csrf_exempt
def paystack_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    raw_body = request.body
    signature = request.headers.get("x-paystack-signature", "")

    computed_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    event = payload.get("event")
    data = payload.get("data", {})
    reference = data.get("reference")

    if event == "charge.success" and reference:
        try:
            payment = Payment.objects.select_related("plan", "pharmacy").get(reference=reference)

            # Prevent duplicate processing
            if payment.status != "success":
                payment.status = "success"
                payment.gateway_response = data.get("gateway_response", "")
                payment.paid_at = timezone.now()
                payment.save(update_fields=["status", "gateway_response", "paid_at"])

                create_subscription(
                    pharmacy=payment.pharmacy,
                    plan=payment.plan,
                    status="active"
                )
        except Payment.DoesNotExist:
            pass

    return HttpResponse("OK")