from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum
from weasyprint import HTML, CSS
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from dateutil.parser import parse
from analytics.models import Order, OrderProduct


class GetSalesReportView(APIView):
    @swagger_auto_schema(
        operation_description="Generate a sales report PDF for a specified date range. "
                             "The report includes total revenue, total orders, top 5 customers by revenue, "
                             "and the most popular product by quantity sold. If no dates are provided, "
                             "defaults to the last 30 days.",
        manual_parameters=[
            openapi.Parameter(
                name="start_date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                description="Start date for the report in YYYY-MM-DD format (optional, defaults to 30 days before end_date).",
                required=False,
                example="2023-01-01",
            ),
            openapi.Parameter(
                name="end_date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                description="End date for the report in YYYY-MM-DD format (optional, defaults to today).",
                required=False,
                example="2023-01-31",
            ),
        ],
        responses={
            200: openapi.Response(
                description="A PDF file containing the sales report.",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="PDF file with sales report data.",
                ),
            ),
            400: openapi.Response(description="Invalid date format."),
            401: openapi.Response(description="Authentication required."),
            500: openapi.Response(description="Internal server error."),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            start_date_str = request.query_params.get("start_date")
            end_date_str = request.query_params.get("end_date")

            if not end_date_str:
                end_date = timezone.now().date()
            else:
                end_date = parse(end_date_str).date()

            if not start_date_str:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = parse(start_date_str).date()

            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())
            )
            end_datetime = timezone.make_aware(
                datetime.combine(end_date, datetime.max.time())
            )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        relevant_statuses = [Order.StatusChoices.CONFIRMED, Order.StatusChoices.SHIPPED]
        orders_in_period = (
            Order.objects.filter(
                created_at__range=[start_datetime, end_datetime],
                status__in=relevant_statuses,
            )
            .select_related("user")
            .prefetch_related("products__product")
        )

        total_revenue = 0
        customer_revenue = defaultdict(float)
        for order in orders_in_period:
            order.calculated_total = order.calculate_total()
            total_revenue += float(order.calculated_total)
            client_name = order.user.get_full_name()
            customer_revenue[client_name] += float(order.calculated_total)

        top_customers = sorted(
            customer_revenue.items(), key=lambda item: item[1], reverse=True
        )[:5]
        top_customers_list = [
            {"name": name, "total": total} for name, total in top_customers
        ]

        total_orders_count = orders_in_period.count()

        most_popular_product = (
            OrderProduct.objects.filter(order__in=orders_in_period)
            .values("product__name")
            .annotate(total_quantity_sold=Sum("quantity"))
            .order_by("-total_quantity_sold")
            .first()
        )

        context = {
            "start_date": start_date,
            "end_date": end_date,
            "all_orders": orders_in_period,
            "total_revenue": total_revenue,
            "total_orders_count": total_orders_count,
            "most_popular_product": most_popular_product,
            "top_customers": top_customers_list,
            "report_date": timezone.now().strftime("%Y-%m-%d"),
        }

        html_string = render_to_string("index.html", context)
        css_path = finders.find("css/output.css")
        if not css_path:
            print(css_path)
            return Response(
                {"error": "CSS file not found at static/css/output.css."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        pdf_file = HTML(
            string=html_string, base_url=request.build_absolute_uri("/")
        ).write_pdf(stylesheets=[CSS(filename=css_path)])

        response = HttpResponse(content_type="application/pdf")
        filename = f"sales_report_{start_date}_to_{end_date}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf_file)
        return response


# @login_required # Ensure user is logged in
def get_sales_html(request):
    try:
        start_date_str = request.GET.get("start_date") # Use request.GET for query parameters in function-based views
        end_date_str = request.GET.get("end_date")

        if not end_date_str:
            end_date = timezone.now().date()
        else:
            end_date = parse(end_date_str).date()

        if not start_date_str:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = parse(start_date_str).date()

        start_datetime = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(end_date, datetime.max.time())
        )
    except ValueError:
        return HttpResponse(
            "Invalid date format. Use YYYY-MM-DD.",
            status=400 # Bad Request status code
        )

    relevant_statuses = [Order.StatusChoices.CONFIRMED, Order.StatusChoices.SHIPPED]
    orders_in_period = (
        Order.objects.filter(
            created_at__range=[start_datetime, end_datetime],
            status__in=relevant_statuses,
        )
        .select_related("user")
        .prefetch_related("products__product")
    )

    total_revenue = 0
    customer_revenue = defaultdict(float)
    for order in orders_in_period:
        order.calculated_total = order.calculate_total()
        total_revenue += float(order.calculated_total)
        client_name = order.user.get_full_name() or order.user.email
        customer_revenue[client_name] += float(order.calculated_total)

    top_customers = sorted(
        customer_revenue.items(), key=lambda item: item[1], reverse=True
    )[:5]
    top_customers_list = [
        {"name": name, "total": total} for name, total in top_customers
    ]

    total_orders_count = orders_in_period.count()

    most_popular_product = (
        OrderProduct.objects.filter(order__in=orders_in_period)
        .values("product__name")
        .annotate(total_quantity_sold=Sum("quantity"))
        .order_by("-total_quantity_sold")
        .first()
    )

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "all_orders": orders_in_period,
        "total_revenue": total_revenue,
        "total_orders_count": total_orders_count,
        "most_popular_product": most_popular_product,
        "top_customers": top_customers_list,
        "report_date": timezone.now().strftime("%Y-%m-%d"),
    }

    return render(request, "index.html", context)