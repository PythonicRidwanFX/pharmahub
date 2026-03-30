import uuid
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

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

    reference = f"PHARM_{uuid.uuid4().hex[:16].upper()}"

    payment = Payment.objects.create(
        pharmacy=request.user.pharmacy,
        plan=plan,
        amount=plan.price,
        reference=reference,
        email=request.user.email,
        status='pending',
        payment_gateway='paystack',
        currency='NGN',
    )

    callback_url = request.build_absolute_uri(reverse('paystack_callback'))

    try:
        amount_kobo = int(Decimal(plan.price) * 100)

        response = initialize_transaction(
            email=request.user.email,
            amount_kobo=amount_kobo,
            reference=reference,
            callback_url=callback_url,
            metadata={
                "payment_id": payment.id,
                "plan_id": plan.id,
                "pharmacy_id": request.user.pharmacy.id,
                "pharmacy_name": request.user.pharmacy.name,
            }
        )

        authorization_url = response.get("authorization_url")
        access_code = response.get("access_code")

        if not authorization_url:
            payment.status = 'failed'
            payment.gateway_response = 'No authorization URL returned by Paystack'
            payment.save(update_fields=['status', 'gateway_response'])
            messages.error(request, 'Unable to start payment.')
            return redirect('plan_list')

        payment.access_code = access_code
        payment.payment_link = authorization_url
        payment.gateway_response = "Payment initialized successfully"
        payment.save(update_fields=['access_code', 'payment_link', 'gateway_response'])

        return redirect(authorization_url)

    except PaystackError as e:
        payment.status = 'failed'
        payment.gateway_response = str(e)
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, f'Unable to start payment: {e}')
        return redirect('plan_list')

    except Exception as e:
        payment.status = 'failed'
        payment.gateway_response = str(e)
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, f'Unexpected payment error: {e}')
        return redirect('plan_list')


@login_required
def paystack_callback(request):
    reference = request.GET.get('reference')
    trxref = request.GET.get('trxref')

    payment_reference = reference or trxref

    if not payment_reference:
        messages.error(request, 'Missing payment reference.')
        return redirect('plan_list')

    payment = get_object_or_404(
        Payment,
        reference=payment_reference,
        pharmacy=request.user.pharmacy
    )

    if payment.status == 'success':
        messages.success(request, 'Payment already verified.')
        return redirect('subscription_status')

    try:
        verified = verify_transaction(payment_reference)

        verified_status = verified.get('status')
        verified_reference = verified.get('reference')
        verified_currency = verified.get('currency', 'NGN')

        try:
            verified_amount = Decimal(str(verified.get('amount', 0))) / Decimal('100')
        except (InvalidOperation, TypeError):
            verified_amount = Decimal('0')

        payment.gateway_response = verified.get('gateway_response', '') or verified.get('message', '')

        if (
            verified_status == 'success'
            and verified_reference == payment.reference
            and verified_currency == payment.currency
            and verified_amount == payment.amount
        ):
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
        payment.gateway_response = str(e)
        payment.save(update_fields=['gateway_response'])
        messages.error(request, f'Payment verification failed: {e}')
        return redirect('plan_list')

    except Exception as e:
        payment.gateway_response = str(e)
        payment.save(update_fields=['gateway_response'])
        messages.error(request, f'Unexpected verification error: {e}')
        return redirect('plan_list')