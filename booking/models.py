from django.db import models

from django.core.exceptions import ValidationError


class Room(models.Model):
    name = models.CharField(max_length=80, unique=True)
    # row = models.PositiveIntegerField(default=10)
    # column = models.PositiveIntegerField(default=8)

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    movie_image = models.ImageField(upload_to='movie_image')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    start_time = models.DateTimeField()

    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def __str__(self):
        return f"{self.title} at {self.start_time}"


class Seat(models.Model):
    row = models.PositiveIntegerField()
    column = models.PositiveIntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, blank=True)
    is_booked = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Seat'
        verbose_name_plural = 'Seats'

    def __str__(self):
        return f"Row {self.row}, Seat {self.column}"

    def clean(self):

        if not isinstance(self.column, int) or not isinstance(self.row, int):
            raise ValidationError("Row and column must be integers.")
        if self.row > 10:
            raise ValidationError("Row must not be larger than 10.")
        if self.column > 9:
            raise ValidationError("Column must not be larger than 9.")
