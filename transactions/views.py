from django.db import transaction
from django.shortcuts import render
from . import models
from transactions.forms import PointsTransferForm
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def points_transfer(request):
    if request.method == 'POST':
        form = PointsTransferForm(request.POST)

        if form.is_valid():

            src_username = form.cleaned_data["enter_your_username"]
            dst_username = form.cleaned_data["enter_destination_username"]
            points_to_transfer = form.cleaned_data["enter_points_to_transfer"]

            with transaction.atomic():
                src_points = models.Points.objects.select_for_update().get(name__username=src_username)
                dst_points = models.Points.objects.select_for_update().get(name__username=dst_username)

                src_points.points -= points_to_transfer
                dst_points.points += points_to_transfer
                src_points.save()
                dst_points.save()

        return render(request, "transactions/points.html", {"src_points": src_points.points, "dst_points": dst_points.points, "src_username": src_username, "dst_username": dst_username})

    else:
        form = PointsTransferForm()

    return render(request, "transactions/pointstransfer.html", {"form": form})
