import json
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

import requests

from .models import Plan, Subscription, Payment
from .utils import create_subscription


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


def flutterwave_headers():
    return {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_flutterwave_payment(payload):
    url = f"{settings.FLW_BASE_URL}/payments"
    response = requests.post(url, json=payload, headers=flutterwave_headers(), timeout=60)
    data = response.json()

    if response.status_code not in [200, 201]:
        message = data.get("message", "Unable to initialize payment")
        raise Exception(message)

    return data


def verify_flutterwave_payment(transaction_id):
    url = f"{settings.FLW_BASE_URL}/transactions/{transaction_id}/verify"
    response = requests.get(url, headers=flutterwave_headers(), timeout=60)
    data = response.json()

    if response.status_code != 200:
        message = data.get("message", "Unable to verify payment")
        raise Exception(message)

    return data


@login_required
def choose_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)

    reference = f"PHARM_{uuid.uuid4().hex[:16].upper()}"

    payment = Payment.objects.create(
        pharmacy=request.user.pharmacy,
        plan=plan,
        amount=plan.price,
        reference=reference,
        email=request.user.email,
        status='pending',
        payment_gateway='flutterwave',
        flutterwave_tx_ref=reference,
        currency='NGN',
    )

    callback_url = request.build_absolute_uri(reverse('payment_callback'))

    payload = {
        "tx_ref": reference,
        "amount": str(plan.price),
        "currency": "NGN",
        "redirect_url": callback_url,
        "payment_options": "card,banktransfer,ussd",
        "customer": {
            "email": request.user.email,
            "name": request.user.get_full_name() or request.user.username,
        },
        "customizations": {
            "title": "PharmaHub Subscription",
            "description": f"Payment for {plan.name} plan",
        },
        "meta": {
            "pharmacy_id": request.user.pharmacy.id,
            "plan_id": plan.id,
            "payment_id": payment.id,
        }
    }

    try:
        data = initialize_flutterwave_payment(payload)

        payment_link = data.get("data", {}).get("link")
        if not payment_link:
            payment.status = 'failed'
            payment.gateway_response = data.get("message", "No payment link returned")
            payment.save(update_fields=['status', 'gateway_response'])
            messages.error(request, 'Unable to start payment.')
            return redirect('plan_list')

        payment.payment_link = payment_link
        payment.access_code = payment_link
        payment.gateway_response = data.get("message", "")
        payment.save(update_fields=['payment_link', 'access_code', 'gateway_response'])

        return redirect(payment_link)

    except Exception as e:
        payment.status = 'failed'
        payment.gateway_response = str(e)
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, f'Unable to start payment: {e}')
        return redirect('plan_list')


@login_required
def payment_callback(request):
    status = request.GET.get('status')
    transaction_id = request.GET.get('transaction_id')
    tx_ref = request.GET.get('tx_ref')

    if not tx_ref:
        messages.error(request, 'Missing payment reference.')
        return redirect('plan_list')

    payment = get_object_or_404(
        Payment,
        reference=tx_ref,
        pharmacy=request.user.pharmacy
    )

    if payment.status == 'success':
        messages.success(request, 'Payment already verified.')
        return redirect('subscription_status')

    if status != 'successful' or not transaction_id:
        payment.status = 'failed' if status == 'failed' else 'cancelled'
        payment.gateway_response = status or 'Payment not completed'
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, 'Payment was not completed.')
        return redirect('plan_list')

    try:
        verified = verify_flutterwave_payment(transaction_id)
        data = verified.get('data', {})

        verified_status = data.get('status')
        verified_amount = Decimal(str(data.get('amount', '0')))
        verified_currency = data.get('currency')
        verified_tx_ref = data.get('tx_ref')

        payment.gateway_response = data.get('processor_response', '') or verified.get('message', '')
        payment.flutterwave_tx_id = str(data.get('id'))
        payment.flutterwave_tx_ref = verified_tx_ref

        if (
            verified_status == 'successful'
            and verified_tx_ref == payment.reference
            and verified_currency == payment.currency
            and verified_amount == payment.amount
        ):
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.save(update_fields=[
                'status',
                'paid_at',
                'gateway_response',
                'flutterwave_tx_id',
                'flutterwave_tx_ref',
            ])

            create_subscription(
                pharmacy=request.user.pharmacy,
                plan=payment.plan,
                status='active'
            )

            messages.success(request, 'Payment verified successfully. Subscription activated.')
            return redirect('subscription_status')

        payment.status = 'failed'
        payment.save(update_fields=[
            'status',
            'gateway_response',
            'flutterwave_tx_id',
            'flutterwave_tx_ref',
        ])
        messages.error(request, 'Payment verification failed or amount mismatch.')
        return redirect('plan_list')

    except Exception as e:
        messages.error(request, f'Payment verification failed: {e}')
        return redirect('plan_list')


@csrf_exempt
def flutterwave_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    secret_hash = getattr(settings, "FLW_WEBHOOK_SECRET_HASH", "")
    signature = request.headers.get("verif-hash", "")

    if not secret_hash or signature != secret_hash:
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    event = payload.get("event")
    data = payload.get("data", {})
    tx_ref = data.get("tx_ref")
    transaction_id = data.get("id")

    if event and tx_ref and transaction_id:
        try:
            payment = Payment.objects.select_related("plan", "pharmacy").get(reference=tx_ref)

            if payment.status != "success":
                verified = verify_flutterwave_payment(transaction_id)
                verified_data = verified.get("data", {})

                verified_status = verified_data.get("status")
                verified_amount = Decimal(str(verified_data.get("amount", "0")))
                verified_currency = verified_data.get("currency")
                verified_tx_ref = verified_data.get("tx_ref")

                if (
                    verified_status == 'successful'
                    and verified_tx_ref == payment.reference
                    and verified_currency == payment.currency
                    and verified_amount == payment.amount
                ):
                    payment.status = "success"
                    payment.gateway_response = verified_data.get("processor_response", "") or "Webhook verified"
                    payment.paid_at = timezone.now()
                    payment.flutterwave_tx_id = str(verified_data.get("id"))
                    payment.flutterwave_tx_ref = verified_tx_ref
                    payment.save(update_fields=[
                        "status",
                        "gateway_response",
                        "paid_at",
                        "flutterwave_tx_id",
                        "flutterwave_tx_ref",
                    ])

                    create_subscription(
                        pharmacy=payment.pharmacy,
                        plan=payment.plan,
                        status="active"
                    )
                else:
                    payment.status = "failed"
                    payment.gateway_response = "Webhook verification failed"
                    payment.save(update_fields=["status", "gateway_response"])

        except Payment.DoesNotExist:
            pass

    return HttpResponse("OK")