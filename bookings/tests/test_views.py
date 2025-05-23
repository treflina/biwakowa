import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ..models import Booking
from ..views import calendars, success
from .base import anonymous_user_redirected_to_login


@pytest.mark.django_db
class TestBookingsListView:
    url = reverse("bookings_app:bookings")
    login_url = reverse("login")

    def test_anonymous_user_redirected_to_login(self, client):
        anonymous_user_redirected_to_login(client, self.url, self.login_url)

    def test_view_page_loads(self, client, user):
        client.force_login(user)
        resp = client.get(self.url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "bookings/bookings.html")

    @pytest.mark.usefixtures("req")
    @pytest.mark.parametrize("req", ["htmx"], indirect=True)
    @pytest.mark.django_db
    def test_htmx_template_is_rendered(self, client, req, user):
        url = reverse("bookings_app:bookings")
        client.force_login(user)
        resp = client.get(url)
        assertTemplateUsed(resp, "bookings/fragments/booking-table.html")


@pytest.mark.django_db
class TestBookingCreateView:

    url = reverse("bookings_app:add_booking")
    login_url = reverse("login")

    def test_anonymous_user_redirected_to_login(self, client):
        anonymous_user_redirected_to_login(client, self.url, self.login_url)

    def test_booking_create_view_post_should_succeed(
        self, apartment, user, client
    ):
        client.force_login(user)
        resp = client.post(
            self.url,
            data={
                "apartment": apartment.id,
                "date_from": date(2024, 7, 1),
                "date_to": date(2024, 7, 8),
            },
            follow=True,
        )

        assert not resp.context["form"].errors
        assert Booking.objects.last().date_from == date(2024, 7, 1)
        assertTemplateUsed(resp, "bookings/bookings.html")

    def test_booking_create_view_post_should_fail(
        self, client, user, apartment
    ):
        client.force_login(user)
        resp = client.post(
            self.url,
            data={
                "apartment": apartment.id,
                "date_from": date(2024, 7, 1),
                "date_to": date(2024, 6, 30),
            },
            follow=True,
        )

        assert resp.context["form"].errors
        assertTemplateUsed(resp, "bookings/add-booking.html")


@pytest.mark.django_db
class TestBookingUpdateView:

    login_url = reverse("login")

    def test_anonymous_user_redirected_to_login(
        self, client, booking_to_update
    ):
        url = reverse(
            "bookings_app:update_booking", kwargs={"pk": booking_to_update.id}
        )
        anonymous_user_redirected_to_login(client, url, self.login_url)

    def test_view_page_loads(self, client, user, booking_to_update):
        url = reverse(
            "bookings_app:update_booking", kwargs={"pk": booking_to_update.id}
        )
        client.force_login(user)
        resp = client.get(url)

        arrival = booking_to_update.date_from.strftime("%Y-%m-%d")
        departure = booking_to_update.date_to.strftime("%Y-%m-%d")
        guest = booking_to_update.guest

        assert resp.status_code == 200
        assertTemplateUsed(resp, "bookings/add-booking.html")
        assert resp.context["form"]["date_from"].value() == arrival
        assert resp.context["form"]["date_to"].value() == departure
        assert resp.context["form"]["guest"].value() == guest
        assert resp.context["updating"] is True

    def test_error_when_bookings_overlapping(
        self, client, user, apartment, booking_to_update
    ):

        url = reverse(
            "bookings_app:update_booking", kwargs={"pk": booking_to_update.id}
        )
        client.force_login(user)

        data = booking_to_update.as_dict()
        data_cleaned = {k: v for k, v in data.items() if v is not None}
        data_cleaned["apartment"] = data_cleaned["apartment"].id
        data_cleaned["date_to"] = date(2024, 7, 15)

        resp = client.post(url, data=data_cleaned)

        booking_to_update.refresh_from_db()
        obj = Booking.objects.get(id=booking_to_update.id)

        assert resp.status_code == 302
        assert obj.date_to == date(2024, 7, 15)

    def test_bookings_periods_overlapping(
        self, apartment, booking, booking_factory, client, user
    ):
        booking = booking_factory(
            apartment=apartment,
            date_from=date(2024, 7, 1),
            date_to=date(2024, 7, 7),
        )
        booking_to_update = booking_factory(
            apartment=booking.apartment,
            date_from=date(2024, 7, 7),
            date_to=date(2024, 7, 10),
        )
        url = reverse(
            "bookings_app:update_booking", kwargs={"pk": booking_to_update.id}
        )
        client.force_login(user)

        data = booking_to_update.as_dict()
        data_cleaned = {k: v for k, v in data.items() if v is not None}
        data_cleaned["apartment"] = data_cleaned["apartment"].id
        data_cleaned["date_from"] = date(2024, 7, 6)

        resp = client.post(url, data=data_cleaned)
        booking_to_update.refresh_from_db()

        obj = Booking.objects.get(id=booking_to_update.id)

        assert obj.date_from != date(2024, 7, 6)
        assert b"alert" in resp.content


@pytest.mark.django_db
class TestDeleteBooking:

    login_url = reverse("login")

    def test_anonymous_user_redirected_to_login(self, client, booking):
        url = reverse("bookings_app:delete_booking", kwargs={"pk": booking.id})
        anonymous_user_redirected_to_login(client, url, self.login_url)

    def test_delete_booking_succeed(self, booking, client, user):
        url = reverse("bookings_app:delete_booking", kwargs={"pk": booking.id})
        client.force_login(user)
        client.post(url, follow=True)

        assertTemplateUsed("bookings/bookings.html")
        assert Booking.objects.filter(id=booking.id).exists() is not True


@pytest.mark.django_db
class TestBookingDetailView:

    login_url = reverse("login")

    def test_anonymous_user_redirected_to_login(self, client, booking):
        url = reverse("bookings_app:booking", kwargs={"pk": booking.id})
        anonymous_user_redirected_to_login(client, url, self.login_url)

    def test_page_load_succeed(self, booking, client, user):
        url = reverse("bookings_app:booking", kwargs={"pk": booking.id})
        client.force_login(user)
        resp = client.get(url)

        assert resp.status_code == 200
        assert bytes(str(booking.guest), encoding="utf-8") in resp.content


@pytest.mark.django_db
class TestCalendars:
    def test_calendars_context(self, apartment_factory, client):
        apartment_factory(name="1")
        apartment_factory(name="2")

        url = reverse(
            "bookings_app:calendars", kwargs={"year": 2024, "month": 7}
        )
        resp = client.get(url)

        assert resp.status_code == 200
        assert resp.context["ap1_dates"] is not None
        assert resp.context["ap2_dates"] is not None
        assert resp.context["num_days"] == range(1, 32)
        assert resp.context["next_year"] == 2024
        assert resp.context["next_month"] == 8
        assert resp.context["first_day"] == 0

    def test_current_month_displayed(self, client):
        url = reverse("bookings_app:calendars")
        resp = client.get(url)

        assert resp.status_code == 200
        assert resp.context["year"] == date.today().year
        assert resp.context["month"] == date.today().month


@pytest.mark.django_db
class TestUpcomingBookingsListView:

    url = reverse("bookings_app:upcoming_bookings")
    login_url = reverse("login")

    def test_anonymous_user_redirected_to_login(self, client):
        anonymous_user_redirected_to_login(client, self.url, self.login_url)

    @pytest.mark.usefixtures("req")
    @pytest.mark.parametrize("req", ["htmx"], indirect=True)
    def test_htmx_template_is_rendered(self, client, req, user):
        client.force_login(user)
        resp = client.get(self.url)
        assertTemplateUsed(resp, "bookings/fragments/booking-table.html")

    def test_page_context_and_template(self, client, user):
        client.force_login(user)
        resp = client.get(self.url)

        assertTemplateUsed(resp, "bookings/bookings.html")
        assert resp.context["upcoming"]


# class TestSuccessPage(TestCase):
#     def setUp(self):
#         from django.contrib.sessions.middleware import SessionMiddleware

#         self.request = RequestFactory().get("/", {"session_id": "cs_num_test"})
#         middleware = SessionMiddleware(lambda x: None)
#         middleware.process_request(self.request)
#         self.request.session["email"] = "test@example.com"
#         self.request.session.save()

#     def test_success_page_loads(self):
#         resp = self.client.get(reverse("bookings_app:success"))
#         assert resp.status_code == 200

#     def test_session_data_stored(self):
#         calendars(self.request)
#         assert self.request.session["email"] == "test@example.com"

#     def test_success_clears_session_email(self):
#         success(self.request)
#         with pytest.raises(KeyError):
#             self.request.session["email"]


# @pytest.mark.django_db
# class TestStripeWebhook:
#     def test_no_http_signature_response_403(self, client):
#         with open(
#             "bookings/tests/stripe_mock_responses/sessioncompleted.json"
#         ) as f:
#             data = json.load(f)
#             resp = client.post(
#                 reverse("bookings_app:webhook"),
#                 data=data,
#                 content_type="application/json",
#             )

#         assert resp.status_code == 403

#     def test_invalid_http_signature_response_400(self, client):
#         with open(
#             "bookings/tests/stripe_mock_responses/sessioncompleted.json"
#         ) as f:
#             data = json.load(f)
#             resp = client.post(
#                 reverse("bookings_app:webhook"),
#                 data=data,
#                 content_type="application/json",
#                 HTTP_STRIPE_SIGNATURE="dummy",
#             )

#         assert resp.status_code == 400

#     def test_valid_session_completed_webhook(
#         self,
#         client,
#         mock_stripe_verify_header,
#         mock_stripe_session_retrieve_paid,
#         booking_factory,
#     ):
#         booking = booking_factory(stripe_checkout_id="cs_test_a1r4DLKrmkYjW4N")

#         with open(
#             "bookings/tests/stripe_mock_responses/sessioncompleted.json"
#         ) as f:
#             data = json.load(f)
#             resp = client.post(
#                 reverse("bookings_app:webhook"),
#                 data=data,
#                 content_type="application/json",
#                 HTTP_STRIPE_SIGNATURE="ignored",
#             )
#         booking.refresh_from_db()

#         assert resp.status_code == 200
#         assert booking.stripe_transaction_status == "success"
#         assert booking.paid is True

#     def test_valid_session_expired_webhook(
#         self, client, mock_stripe_verify_header, booking_factory
#     ):
#         booking_factory(stripe_checkout_id="cs_test_a1j46z4")

#         with open(
#             "bookings/tests/stripe_mock_responses/sessionexpired.json"
#         ) as f:
#             data = json.load(f)
#             resp = client.post(
#                 reverse("bookings_app:webhook"),
#                 data=data,
#                 content_type="application/json",
#                 HTTP_STRIPE_SIGNATURE="ignored",
#             )

#         assert resp.status_code == 200
#         assert not Booking.objects.filter(
#             stripe_checkout_id="cs_test_a1j46z4"
#         ).exists()


# @pytest.mark.django_db
# class TestOnlineBooking:

#     url = reverse(
#         "bookings_app:onlinebooking",
#         kwargs={"arrival": "2044-09-03", "departure": "2044-07-09", "pk": "1"},
#     )

#     data = {
#         "pk": 1,
#         "name": "Test Guest",
#         "email": "test@example.com",
#         "phone": "8709079070",
#         "arrival": date(2044, 9, 3),
#         "departure": date(2044, 9, 9),
#         "guest_notes": "my wish",
#         "consent": True,
#     }

#     def test_invalid_stripe_product_id_handled(
#         self, client, apartment_factory, mock_stripe_session_create_error
#     ):
#         apartment_factory(id=1, stripe_product_id="id_000")
#         resp = client.post(self.url, data=self.data, follow=True)

#         assert resp.status_code == 200
#         assertTemplateUsed("bookings/bookings-search.html")
#         assert len(mail.outbox) > 0
#         assert mail.outbox[0].subject == (
#             "Error while creating checkout session or db saving"
#         )

#     def test_no_stripe_product_id_handled(self, client, apartment_factory):
#         apartment_factory(id=1, stripe_product_id=None)
#         resp = client.post(self.url, data=self.data, follow=True)

#         assert resp.status_code == 200
#         assertTemplateUsed("bookings/bookings-search.html")
#         assert len(mail.outbox) > 0
#         assert mail.outbox[0].subject == ("Error. No stripe product_id")

#     def test_stripe_connection_error(
#         self,
#         client,
#         apartment_factory,
#         phone_snippet,
#         mock_stripe_connection_error,
#     ):
#         apartment_factory(id=1, stripe_product_id="id_000")
#         resp = client.post(self.url, data=self.data, follow=True)

#         assert resp.status_code == 200
#         assertTemplateUsed("bookings/bookings-search.html")
#         assert phone_snippet.phone in str(resp.content)

#     def test_booking_created(self, apartment_factory, client):
#         apartment_factory(id=1, stripe_product_id="id_000")

#         with patch("stripe.checkout.Session.create") as checkout_create:
#             mock_resp_obj = MagicMock(status_code=200)
#             mock_resp_obj.id = "cs_test_a11YY"
#             checkout_create.return_value = mock_resp_obj
#             client.post(self.url, data=self.data)

#         booking = Booking.objects.get(stripe_checkout_id="cs_test_a11YY")
#         assert booking.stripe_transaction_status == "pending"


# @pytest.mark.django_db
# class TestCancelPage:

#     url = reverse("bookings_app:cancel")

#     def test_cancel_page_loads(self, client, phone_snippet):

#         with patch("stripe.checkout.Session.retrieve") as mock_retrieve:
#             mock_resp = MagicMock()
#             mock_resp.url = "https://checkout/id_some"
#             mock_retrieve.return_value = mock_resp
#             resp = client.get(self.url, data={"session_id": "id_some"})

#         assert resp.status_code == 200
#         assert phone_snippet.phone in str(resp.content)
#         assert "https://checkout/id_some" in str(resp.content)


@pytest.mark.django_db
class TestBookingSearch:

    url = reverse("bookings_app:booking-search")

    def test_booking_search_loads(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 200
        assert "form" in resp.context

    def test_booking_search_submitted(self, client):
        resp = client.get(
            self.url,
            {"arrival": "19.07.2026", "departure": "26.07.2026", "submit": ""},
        )
        assert resp.status_code == 200
        assert "available_apartments" in resp.context
        assert "arrival" in resp.context
        assert "departure" in resp.context
        assert "num_nights" in resp.context
        assert "results" in resp.context
