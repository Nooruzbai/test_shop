from django.urls import path

from report.views import GetSalesReportView, get_sales_html

urlpatterns = [
    path("sales", GetSalesReportView.as_view()),
    path("sales-html/", get_sales_html, name="sales-report-html"),
]
